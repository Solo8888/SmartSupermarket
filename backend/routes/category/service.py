# 商品类别服务
# 处理商品类别相关的业务逻辑

from sqlalchemy.orm import Session
from models.category import Category
from models.user_store import UserStore
from .schemas import CategoryCreate, CategoryUpdate
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from core.exceptions import NotFoundError, ClientError
from sqlalchemy import func


class CategoryService:
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

        # 创建单个分类（所有门店共用）
        category = Category(
            name=payload.name,
            parent_id=payload.parent_id,
            description=payload.description,
            sort_order=payload.sort_order
        )
        db.add(category)
        db.commit()
        db.refresh(category)

        # 为所有门店关联此分类
        from models.store import Store
        from models.store_product import StoreProduct
        import uuid
        
        # 获取所有门店
        stores = db.query(Store).all()
        
        # 为每个门店创建分类关联
        # 注意：分类不需要直接关联门店，通过商品间接关联

        return {
            "id": category.id,
            "name": category.name,
            "parent_id": category.parent_id,
            "description": category.description,
            "sort_order": category.sort_order,
            "created_at": category.created_at,
            "updated_at": category.updated_at
        }

    @staticmethod
    def get_categories(db: Session, params: Params, user = None) -> Page[Category]:
        """
        获取商品类别列表

        Args:
            db: 数据库会话
            params: 分页参数
            user: 当前用户

        Returns:
            商品类别列表（分页）
        """
        # 构建查询
        query = db.query(Category).order_by(Category.sort_order.asc(), Category.id.asc())
        
        # 所有用户都可以查看所有类别（因为分类是共用的）
        
        return sqlalchemy_paginate(query, params=params)
    
    @staticmethod
    def get_all_categories(db: Session, user = None) -> list:
        """
        获取所有商品类别（不分页）

        Args:
            db: 数据库会话
            user: 当前用户

        Returns:
            所有商品类别列表
        """
        # 构建查询
        query = db.query(Category).order_by(Category.sort_order.asc(), Category.id.asc())
        
        # 所有用户都可以查看所有类别（因为分类是共用的）
        
        categories = query.all()
        return [
            {
                "id": cat.id,
                "name": cat.name,
                "parent_id": cat.parent_id,
                "description": cat.description,
                "sort_order": cat.sort_order,
                "created_at": cat.created_at,
                "updated_at": cat.updated_at
            }
            for cat in categories
        ]

    @staticmethod
    def get_category(db: Session, category_id: str, user = None) -> dict:
        """
        获取单个商品类别详情

        Args:
            db: 数据库会话
            category_id: 商品类别ID
            user: 当前用户

        Returns:
            商品类别详情

        Raises:
            NotFoundError: 商品类别不存在
        """
        # 获取商品类别
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise NotFoundError("商品类别不存在")
        
        # 所有用户都可以查看所有类别（因为分类是共用的）

        return {
            "id": category.id,
            "name": category.name,
            "parent_id": category.parent_id,
            "description": category.description,
            "sort_order": category.sort_order,
            "created_at": category.created_at,
            "updated_at": category.updated_at
        }

    @staticmethod
    def update_category(db: Session, category_id: str, payload: CategoryUpdate, user) -> dict:
        """
        更新商品类别

        Args:
            db: 数据库会话
            category_id: 商品类别ID
            payload: 更新商品类别请求体
            user: 当前用户

        Returns:
            更新成功的商品类别信息

        Raises:
            NotFoundError: 商品类别不存在
        """
        # 获取商品类别
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise NotFoundError("商品类别不存在")
        
        # 只有系统管理员可以更新类别
        if user.role != 'system_admin':
            raise ClientError("权限不足，无法更新此类别", "PERMISSION_DENIED")

        # 检查父分类是否存在（如果提供了parent_id）
        if payload.parent_id is not None:
            parent_category = db.query(Category).filter(Category.id == payload.parent_id).first()
            if not parent_category:
                raise ValueError("父分类不存在")

        # 更新字段（只更新提供的字段）
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(category, field, value)

        # 更新时间戳
        category.updated_at = func.current_timestamp()

        db.commit()
        db.refresh(category)

        return {
            "id": category.id,
            "name": category.name,
            "parent_id": category.parent_id,
            "description": category.description,
            "sort_order": category.sort_order,
            "created_at": category.created_at,
            "updated_at": category.updated_at
        }

    @staticmethod
    def delete_category(db: Session, category_id: str, user) -> None:
        """
        删除商品类别

        Args:
            db: 数据库会话
            category_id: 商品类别ID
            user: 当前用户

        Raises:
            NotFoundError: 商品类别不存在
            ClientError: 权限不足
        """
        # 获取商品类别
        category = db.query(Category).filter(Category.id == category_id).first()
        if not category:
            raise NotFoundError("商品类别不存在")
        
        # 只有系统管理员可以删除类别
        if user.role != 'system_admin':
            raise ClientError("权限不足，无法删除此类别", "PERMISSION_DENIED")

        # 删除商品类别
        db.delete(category)
        db.commit()
