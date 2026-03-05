# 商品类别服务
# 处理商品类别相关的业务逻辑

from sqlalchemy.orm import Session
from models.category import Category
from .schemas import CategoryCreate
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate


class CategoryService:
    @staticmethod
    def create_category(db: Session, payload: CategoryCreate, user) -> dict:
        """
        创建商品类别

        Args:
            db: 数据库会话
            payload: 创建商品类别请求体
            user: 当前用户

        Returns:
            创建成功的商品类别信息
        """
        # 检查父分类是否存在
        if payload.parent_id:
            parent_category = db.query(Category).filter(Category.id == payload.parent_id).first()
            if not parent_category:
                raise ValueError("父分类不存在")

        # 创建新商品类别
        category = Category(
            name=payload.name,
            parent_id=payload.parent_id,
            description=payload.description,
            level=payload.level,
            sort_order=payload.sort_order,
            status=payload.status
        )

        db.add(category)
        db.commit()
        db.refresh(category)

        # 转换为字典返回
        return {
            "id": category.id,
            "name": category.name,
            "parent_id": category.parent_id,
            "description": category.description,
            "level": category.level,
            "sort_order": category.sort_order,
            "status": category.status,
            "created_at": category.created_at,
            "updated_at": category.updated_at
        }

    @staticmethod
    def get_categories(db: Session, params: Params) -> Page[Category]:
        """
        获取商品类别列表

        Args:
            db: 数据库会话
            params: 分页参数

        Returns:
            商品类别列表（分页）
        """
        query = db.query(Category).order_by(Category.sort_order.asc(), Category.id.asc())
        return sqlalchemy_paginate(query, params=params)
