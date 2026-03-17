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
