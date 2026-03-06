
# 商品服务
# 处理商品相关的业务逻辑

from sqlalchemy.orm import Session
from models.product import Product
from models.category import Category
from .schemas import ProductCreate
from core.exceptions import NotFoundError
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate


class ProductService:
    @staticmethod
    def create_product(db: Session, payload: ProductCreate, user) -> dict:
        """
        创建商品

        Args:
            db: 数据库会话
            payload: 创建商品请求体
            user: 当前用户

        Returns:
            创建成功的商品信息
        """
        # 检查分类是否存在
        if payload.category_id:
            category = db.query(Category).filter(Category.id == payload.category_id).first()
            if not category:
                raise ValueError("分类不存在")

        # 检查条码是否已存在
        if payload.barcode:
            existing_product = db.query(Product).filter(Product.barcode == payload.barcode).first()
            if existing_product:
                raise ValueError("商品条码已存在")

        # 创建新商品
        product = Product(
            name=payload.name,
            category_id=payload.category_id,
            barcode=payload.barcode,
            description=payload.description,
            price=payload.price,
            cost_price=payload.cost_price,
            image_url=payload.image_url,
            status=payload.status,
            sort_order=payload.sort_order
        )

        db.add(product)
        db.commit()
        db.refresh(product)

        # 转换为字典返回
        return {
            "id": product.id,
            "name": product.name,
            "category_id": product.category_id,
            "barcode": product.barcode,
            "description": product.description,
            "price": product.price,
            "cost_price": product.cost_price,
            "image_url": product.image_url,
            "status": product.status,
            "sort_order": product.sort_order,
            "created_at": product.created_at,
            "updated_at": product.updated_at
        }

    @staticmethod
    def get_products(db: Session, params: Params) -> Page[Product]:
        """
        获取商品列表

        Args:
            db: 数据库会话
            params: 分页参数

        Returns:
            商品列表（分页）
        """
        query = db.query(Product).order_by(Product.sort_order.asc(), Product.id.asc())
        return sqlalchemy_paginate(query, params=params)

