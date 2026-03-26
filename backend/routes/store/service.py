# 门店服务
# 处理门店相关的业务逻辑

from sqlalchemy.orm import Session
from models.store import Store
from .schemas import StoreCreate, StoreUpdate
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from core.exceptions import NotFoundError
from sqlalchemy import func


class StoreService:
    @staticmethod
    def create_store(db: Session, payload: StoreCreate, user) -> dict:
        """
        创建门店

        Args:
            db: 数据库会话
            payload: 创建门店请求体
            user: 当前用户

        Returns:
            创建成功的门店信息
        """
        # 创建新门店
        store = Store(
            name=payload.name,
            address=payload.address,
            phone=payload.phone,
            opening_hours=payload.opening_hours,
            status=payload.status
        )

        db.add(store)
        db.commit()
        db.refresh(store)

        # 为新门店关联所有现有商品
        from models.product import Product
        from models.store_product import StoreProduct
        from models.inventory import Inventory
        import uuid
        
        # 获取所有商品
        all_products = db.query(Product).all()
        
        # 为每个商品创建门店商品关联
        for product in all_products:
            # 检查关联是否已存在
            existing_association = db.query(StoreProduct).filter(
                StoreProduct.store_id == store.id,
                StoreProduct.product_id == product.id
            ).first()
            
            if not existing_association:
                # 创建门店商品关联
                store_product = StoreProduct(
                    id=str(uuid.uuid4()),
                    store_id=store.id,
                    product_id=product.id,
                    status='active'
                )
                db.add(store_product)
            
            # 检查是否已有库存记录
            existing_inventory = db.query(Inventory).filter(
                Inventory.product_id == product.id
            ).first()
            
            if not existing_inventory:
                # 为商品创建库存记录
                inventory = Inventory(
                    id=str(uuid.uuid4()),
                    product_id=product.id,
                    stock_quantity=0,
                    warning_quantity=10
                )
                db.add(inventory)
        
        db.commit()

        # 转换为字典返回
        return {
            "id": store.id,
            "name": store.name,
            "address": store.address,
            "phone": store.phone,
            "opening_hours": store.opening_hours,
            "status": store.status,
            "created_at": store.created_at,
            "updated_at": store.updated_at
        }
    
    @staticmethod
    def get_stores(db: Session, params: Params) -> Page[Store]:
        """
        获取门店列表

        Args:
            db: 数据库会话
            params: 分页参数

        Returns:
            门店列表（分页）
        """
        query = db.query(Store).order_by(Store.created_at.desc())
        return sqlalchemy_paginate(query, params=params)
    
    @staticmethod
    def get_all_stores(db: Session) -> list:
        """
        获取所有门店（不分页）

        Args:
            db: 数据库会话

        Returns:
            所有门店列表
        """
        stores = db.query(Store).order_by(Store.created_at.desc()).all()
        return [
            {
                "id": store.id,
                "name": store.name,
                "address": store.address,
                "phone": store.phone,
                "opening_hours": store.opening_hours,
                "status": store.status,
                "created_at": store.created_at,
                "updated_at": store.updated_at
            }
            for store in stores
        ]
    
    @staticmethod
    def get_store(db: Session, store_id: str) -> dict:
        """
        获取单个门店详情

        Args:
            db: 数据库会话
            store_id: 门店ID

        Returns:
            门店详情

        Raises:
            NotFoundError: 门店不存在
        """
        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            raise NotFoundError("门店不存在")

        return {
            "id": store.id,
            "name": store.name,
            "address": store.address,
            "phone": store.phone,
            "opening_hours": store.opening_hours,
            "status": store.status,
            "created_at": store.created_at,
            "updated_at": store.updated_at
        }
    
    @staticmethod
    def update_store(db: Session, store_id: str, payload: StoreUpdate, user) -> dict:
        """
        更新门店

        Args:
            db: 数据库会话
            store_id: 门店ID
            payload: 更新门店请求体
            user: 当前用户

        Returns:
            更新成功的门店信息

        Raises:
            NotFoundError: 门店不存在
        """
        # 获取门店
        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            raise NotFoundError("门店不存在")

        # 更新字段（只更新提供的字段）
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(store, field, value)

        # 更新时间戳
        store.updated_at = func.current_timestamp()

        db.commit()
        db.refresh(store)

        return {
            "id": store.id,
            "name": store.name,
            "address": store.address,
            "phone": store.phone,
            "opening_hours": store.opening_hours,
            "status": store.status,
            "created_at": store.created_at,
            "updated_at": store.updated_at
        }
    
    @staticmethod
    def delete_store(db: Session, store_id: str, user) -> None:
        """
        删除门店

        Args:
            db: 数据库会话
            store_id: 门店ID
            user: 当前用户

        Raises:
            NotFoundError: 门店不存在
        """
        # 获取门店
        store = db.query(Store).filter(Store.id == store_id).first()
        if not store:
            raise NotFoundError("门店不存在")

        # 删除门店
        db.delete(store)
        db.commit()
