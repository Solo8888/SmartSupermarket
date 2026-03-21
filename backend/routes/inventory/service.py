

# 库存服务
# 处理库存相关的业务逻辑

from sqlalchemy.orm import Session
from sqlalchemy import func
from models.inventory import Inventory
from models.product import Product
from models.user_store import UserStore
from .schemas import InventoryUpdate, StockInRequest, StockOutRequest
from core.exceptions import NotFoundError, ClientError
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate


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

