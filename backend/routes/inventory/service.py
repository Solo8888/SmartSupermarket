

# 库存服务
# 处理库存相关的业务逻辑

from sqlalchemy.orm import Session
from sqlalchemy import func
from models.inventory import Inventory
from models.product import Product
from models.user_store import UserStore
from models.store import Store
from .schemas import InventoryUpdate, StockInRequest, StockOutRequest
from core.exceptions import NotFoundError, ClientError
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
import math


class InventoryService:
    @staticmethod
    def get_user_stores(db: Session, user_id: str):
        """
        获取用户关联的门店ID列表

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            门店ID列表
        """
        user_stores = db.query(UserStore).filter(UserStore.user_id == user_id).all()
        return [user_store.store_id for user_store in user_stores]

    @staticmethod
    def get_inventories(db: Session, params: Params, search: str = None, user = None) -> Page[Inventory]:
        """
        获取库存列表

        Args:
            db: 数据库会话
            params: 分页参数
            search: 搜索关键词（可选）
            user: 当前用户

        Returns:
            库存列表（分页）
        """
        # 构建查询
        query = db.query(Inventory).join(Product, Inventory.product_id == Product.id)
        
        # 系统管理员可以查看所有库存，其他用户只能查看关联门店的库存
        if user and user.role != 'system_admin':
            user_store_ids = InventoryService.get_user_stores(db, user.id)
            if user_store_ids:
                query = query.filter(Product.store_id.in_(user_store_ids))
            else:
                # 如果用户没有关联门店，返回空列表
                query = query.filter(Product.store_id.in_([]))
        
        # 搜索条件
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Product.name.like(search_term)) |
                (Product.brand.like(search_term)) |
                (Product.barcode.like(search_term))
            )
        
        # 排序
        query = query.order_by(Inventory.id.asc())
        
        return sqlalchemy_paginate(query, params=params)

    @staticmethod
    def get_inventory(db: Session, product_id: str, user = None) -> dict:
        """
        获取单个商品库存

        Args:
            db: 数据库会话
            product_id: 商品ID
            user: 当前用户

        Returns:
            商品库存信息

        Raises:
            NotFoundError: 库存不存在
            ClientError: 权限不足
        """
        # 获取商品信息，检查门店权限
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise NotFoundError("商品不存在")
        
        # 系统管理员可以查看所有库存，其他用户只能查看关联门店的库存
        if user and user.role != 'system_admin':
            user_store_ids = InventoryService.get_user_stores(db, user.id)
            if product.store_id not in user_store_ids:
                raise ClientError("权限不足，无法查看此商品库存", "PERMISSION_DENIED")
        
        # 获取库存信息
        inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
        if not inventory:
            raise NotFoundError("库存不存在")

        return {
            "id": inventory.id,
            "product_id": inventory.product_id,
            "stock_quantity": inventory.stock_quantity,
            "warning_quantity": inventory.warning_quantity,
            "last_stock_time": inventory.last_stock_time,
            "created_at": inventory.created_at,
            "updated_at": inventory.updated_at
        }

    @staticmethod
    def get_replenishment_suggestions(db: Session, store_id: str = None, category_id: str = None, user = None) -> list[dict]:
        """
        获取补货建议

        Args:
            db: 数据库会话
            store_id: 仓库ID（可选）
            category_id: 商品类别ID（可选）
            user: 当前用户

        Returns:
            补货建议列表
        """
        # 构建查询，关联Inventory和Product表
        query = db.query(Inventory, Product).join(Product, Inventory.product_id == Product.id)
        
        # 系统管理员可以查看所有库存，其他用户只能查看关联门店的库存
        if user and user.role != 'system_admin':
            user_store_ids = InventoryService.get_user_stores(db, user.id)
            if user_store_ids:
                query = query.filter(Product.store_id.in_(user_store_ids))
            else:
                # 如果用户没有关联门店，返回空列表
                return []
        
        # 按仓库筛选
        if store_id:
            query = query.filter(Product.store_id == store_id)
        
        # 按商品类别筛选
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        # 获取所有库存记录
        results = query.all()
        
        suggestions = []
        for inventory, product in results:
            # 计算建议补货量：max(0, safety_stock * 2 - current_stock)
            suggested_replenishment = max(0, inventory.warning_quantity * 2 - inventory.stock_quantity)
            
            suggestions.append({
                "product_id": product.id,
                "product_name": product.name,
                "current_stock": inventory.stock_quantity,
                "safety_stock": inventory.warning_quantity,
                "suggested_replenishment": suggested_replenishment
            })
        
        return suggestions

    @staticmethod
    def get_transfer_plans(db: Session, product_id: str = None, user = None) -> list[dict]:
        """
        获取库存调拨方案

        Args:
            db: 数据库会话
            product_id: 商品ID（可选）
            user: 当前用户

        Returns:
            调拨方案列表
        """
        # 构建查询，获取所有商品在各门店的库存信息
        query = db.query(
            Product.id.label('product_id'),
            Product.name.label('product_name'),
            Product.store_id,
            Store.name.label('store_name'),
            Inventory.stock_quantity,
            Inventory.warning_quantity
        ).join(
            Inventory, Product.id == Inventory.product_id
        ).join(
            Store, Product.store_id == Store.id
        ).filter(
            Store.status == 'active'
        )
        
        # 按商品ID筛选
        if product_id:
            query = query.filter(Product.id == product_id)
        
        # 系统管理员可以查看所有库存，其他用户只能查看关联门店的库存
        if user and user.role != 'system_admin':
            user_store_ids = InventoryService.get_user_stores(db, user.id)
            if user_store_ids:
                query = query.filter(Product.store_id.in_(user_store_ids))
            else:
                # 如果用户没有关联门店，返回空列表
                return []
        
        # 获取所有库存记录
        results = query.all()
        
        # 按商品ID分组，统计每个商品在各门店的库存情况
        product_inventory = {}
        for row in results:
            pid = row.product_id
            if pid not in product_inventory:
                product_inventory[pid] = {
                    'product_id': pid,
                    'product_name': row.product_name,
                    'stores': []
                }
            product_inventory[pid]['stores'].append({
                'store_id': row.store_id,
                'store_name': row.store_name,
                'stock_quantity': row.stock_quantity,
                'warning_quantity': row.warning_quantity
            })
        
        # 生成调拨方案
        transfer_plans = []
        
        for pid, product_data in product_inventory.items():
            stores = product_data['stores']
            
            # 如果只有一个门店，无法调拨
            if len(stores) < 2:
                continue
            
            # 计算平均库存和安全库存
            total_stock = sum(s['stock_quantity'] for s in stores)
            avg_stock = total_stock / len(stores)
            avg_safety_stock = sum(s['warning_quantity'] for s in stores) / len(stores)
            
            # 识别调出门店和调入门店
            from_stores = []  # 库存过剩的门店
            to_stores = []    # 库存不足的门店
            
            for store in stores:
                # 调出门店：库存量 > 平均库存量 + 安全库存
                if store['stock_quantity'] > avg_stock + avg_safety_stock:
                    from_stores.append(store)
                # 调入门店：库存量 < 安全库存
                elif store['stock_quantity'] < store['warning_quantity']:
                    to_stores.append(store)
            
            # 生成调拨方案
            for from_store in from_stores:
                for to_store in to_stores:
                    # 计算调拨数量
                    available_to_transfer = from_store['stock_quantity'] - (avg_stock + avg_safety_stock)
                    needed_quantity = to_store['warning_quantity'] * 2 - to_store['stock_quantity']
                    
                    transfer_quantity = min(
                        max(0, available_to_transfer),
                        max(0, needed_quantity)
                    )
                    
                    # 只有当调拨数量大于0时才生成方案
                    if transfer_quantity > 0:
                        # 生成调拨原因
                        reason = f"{from_store['store_name']}库存过剩({from_store['stock_quantity']}件)，{to_store['store_name']}库存不足({to_store['stock_quantity']}件)"
                        
                        transfer_plans.append({
                            'product_id': product_data['product_id'],
                            'product_name': product_data['product_name'],
                            'from_store_id': from_store['store_id'],
                            'from_store_name': from_store['store_name'],
                            'to_store_id': to_store['store_id'],
                            'to_store_name': to_store['store_name'],
                            'transfer_quantity': transfer_quantity,
                            'reason': reason
                        })
        
        # 按调拨数量从大到小排序
        transfer_plans.sort(key=lambda x: x['transfer_quantity'], reverse=True)
        
        return transfer_plans

    @staticmethod
    def update_inventory(db: Session, product_id: str, payload: InventoryUpdate, user) -> dict:
        """
        更新库存

        Args:
            db: 数据库会话
            product_id: 商品ID
            payload: 更新库存请求体
            user: 当前用户

        Returns:
            更新成功的库存信息

        Raises:
            NotFoundError: 库存不存在
            ClientError: 权限不足
        """
        # 获取商品信息，检查门店权限
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise NotFoundError("商品不存在")
        
        # 系统管理员可以更新所有库存，其他用户只能更新关联门店的库存
        if user.role != 'system_admin':
            user_store_ids = InventoryService.get_user_stores(db, user.id)
            if product.store_id not in user_store_ids:
                raise ClientError("权限不足，无法更新此商品库存", "PERMISSION_DENIED")
        
        # 获取库存信息
        inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
        if not inventory:
            raise NotFoundError("库存不存在")

        # 更新库存
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(inventory, field, value)

        inventory.last_stock_time = func.current_timestamp()
        inventory.updated_at = func.current_timestamp()

        db.commit()
        db.refresh(inventory)

        return {
            "id": inventory.id,
            "product_id": inventory.product_id,
            "stock_quantity": inventory.stock_quantity,
            "warning_quantity": inventory.warning_quantity,
            "last_stock_time": inventory.last_stock_time,
            "created_at": inventory.created_at,
            "updated_at": inventory.updated_at
        }

    @staticmethod
    def stock_in(db: Session, product_id: str, payload: StockInRequest, user) -> dict:
        """
        入库登记

        Args:
            db: 数据库会话
            product_id: 商品ID
            payload: 入库请求体
            user: 当前用户

        Returns:
            更新后的库存信息

        Raises:
            NotFoundError: 商品或库存不存在
            ClientError: 权限不足
        """
        # 获取商品信息，检查门店权限
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise NotFoundError("商品不存在")
        
        # 系统管理员可以操作所有库存，其他用户只能操作关联门店的库存
        if user.role != 'system_admin':
            user_store_ids = InventoryService.get_user_stores(db, user.id)
            if product.store_id not in user_store_ids:
                raise ClientError("权限不足，无法操作此商品库存", "PERMISSION_DENIED")
        
        # 获取或创建库存
        inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
        if not inventory:
            inventory = Inventory(
                product_id=product_id,
                stock_quantity=payload.quantity,
                warning_quantity=10
            )
            db.add(inventory)
        else:
            inventory.stock_quantity += payload.quantity

        inventory.last_stock_time = func.current_timestamp()
        inventory.updated_at = func.current_timestamp()

        db.commit()
        db.refresh(inventory)

        return {
            "id": inventory.id,
            "product_id": inventory.product_id,
            "stock_quantity": inventory.stock_quantity,
            "warning_quantity": inventory.warning_quantity,
            "last_stock_time": inventory.last_stock_time,
            "created_at": inventory.created_at,
            "updated_at": inventory.updated_at
        }

    @staticmethod
    def stock_out(db: Session, product_id: str, payload: StockOutRequest, user) -> dict:
        """
        出库审核

        Args:
            db: 数据库会话
            product_id: 商品ID
            payload: 出库请求体
            user: 当前用户

        Returns:
            更新后的库存信息

        Raises:
            NotFoundError: 库存不存在
            ValueError: 库存不足
            ClientError: 权限不足
        """
        # 获取商品信息，检查门店权限
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise NotFoundError("商品不存在")
        
        # 系统管理员可以操作所有库存，其他用户只能操作关联门店的库存
        if user.role != 'system_admin':
            user_store_ids = InventoryService.get_user_stores(db, user.id)
            if product.store_id not in user_store_ids:
                raise ClientError("权限不足，无法操作此商品库存", "PERMISSION_DENIED")
        
        # 获取库存信息
        inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
        if not inventory:
            raise NotFoundError("库存不存在")

        # 检查库存是否足够
        if inventory.stock_quantity < payload.quantity:
            raise ValueError("库存不足")

        # 更新库存
        inventory.stock_quantity -= payload.quantity
        inventory.last_stock_time = func.current_timestamp()
        inventory.updated_at = func.current_timestamp()

        db.commit()
        db.refresh(inventory)

        return {
            "id": inventory.id,
            "product_id": inventory.product_id,
            "stock_quantity": inventory.stock_quantity,
            "warning_quantity": inventory.warning_quantity,
            "last_stock_time": inventory.last_stock_time,
            "created_at": inventory.created_at,
            "updated_at": inventory.updated_at
        }

