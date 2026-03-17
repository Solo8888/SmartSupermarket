# 门店服务
# 处理门店相关的业务逻辑

from sqlalchemy.orm import Session
from models.store import Store
from .schemas import StoreCreate
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
