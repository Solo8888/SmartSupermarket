
# 商品服务
# 处理商品相关的业务逻辑

from sqlalchemy.orm import Session
from sqlalchemy import func
from models.product import Product
from models.category import Category
from .schemas import ProductCreate, ProductUpdate
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
            price=payload.price,
            original_price=payload.original_price,
            description=payload.description,
            image_url=payload.image_url,
            barcode=payload.barcode,
            brand=payload.brand,
            unit=payload.unit,
            status=payload.status
        )

        db.add(product)
        db.commit()
        db.refresh(product)

        # 转换为字典返回
        return {
            "id": product.id,
            "name": product.name,
            "category_id": product.category_id,
            "price": product.price,
            "original_price": product.original_price,
            "description": product.description,
            "image_url": product.image_url,
            "barcode": product.barcode,
            "brand": product.brand,
            "unit": product.unit,
            "status": product.status,
            "sales_count": product.sales_count,
            "view_count": product.view_count,
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
        query = db.query(Product).order_by(Product.id.asc())
        return sqlalchemy_paginate(query, params=params)
    
    @staticmethod
    def get_all_products(db: Session) -> list:
        """
        获取所有商品（不分页）

        Args:
            db: 数据库会话

        Returns:
            所有商品列表
        """
        products = db.query(Product).order_by(Product.id.asc()).all()
        return [
            {
                "id": product.id,
                "name": product.name,
                "category_id": product.category_id,
                "price": product.price,
                "original_price": product.original_price,
                "description": product.description,
                "image_url": product.image_url,
                "barcode": product.barcode,
                "brand": product.brand,
                "unit": product.unit,
                "status": product.status,
                "sales_count": product.sales_count,
                "view_count": product.view_count,
                "created_at": product.created_at,
                "updated_at": product.updated_at
            }
            for product in products
        ]

    @staticmethod
    def get_product(db: Session, product_id: int) -> dict:
        """
        获取单个商品详情

        Args:
            db: 数据库会话
            product_id: 商品ID

        Returns:
            商品详情

        Raises:
            NotFoundError: 商品不存在
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise NotFoundError("商品不存在")

        return {
            "id": product.id,
            "name": product.name,
            "category_id": product.category_id,
            "price": product.price,
            "original_price": product.original_price,
            "description": product.description,
            "image_url": product.image_url,
            "barcode": product.barcode,
            "brand": product.brand,
            "unit": product.unit,
            "status": product.status,
            "sales_count": product.sales_count,
            "view_count": product.view_count,
            "created_at": product.created_at,
            "updated_at": product.updated_at
        }

    @staticmethod
    def update_product(db: Session, product_id: int, payload: ProductUpdate, user) -> dict:
        """
        更新商品

        Args:
            db: 数据库会话
            product_id: 商品ID
            payload: 更新商品请求体
            user: 当前用户

        Returns:
            更新成功的商品信息

        Raises:
            NotFoundError: 商品不存在
        """
        # 获取商品
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise NotFoundError("商品不存在")

        # 检查分类是否存在（如果提供了category_id）
        if payload.category_id is not None:
            category = db.query(Category).filter(Category.id == payload.category_id).first()
            if not category:
                raise ValueError("分类不存在")

        # 检查条码是否已存在（如果提供了barcode且不是当前商品的barcode）
        if payload.barcode is not None:
            existing_product = db.query(Product).filter(Product.barcode == payload.barcode).filter(Product.id != product_id).first()
            if existing_product:
                raise ValueError("商品条码已存在")

        # 更新字段（只更新提供的字段）
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)

        # 更新时间戳
        product.updated_at = func.current_timestamp()

        db.commit()
        db.refresh(product)

        return {
            "id": product.id,
            "name": product.name,
            "category_id": product.category_id,
            "price": product.price,
            "original_price": product.original_price,
            "description": product.description,
            "image_url": product.image_url,
            "barcode": product.barcode,
            "brand": product.brand,
            "unit": product.unit,
            "status": product.status,
            "sales_count": product.sales_count,
            "view_count": product.view_count,
            "created_at": product.created_at,
            "updated_at": product.updated_at
        }

    @staticmethod
    def delete_product(db: Session, product_id: int, user) -> None:
        """
        删除商品

        Args:
            db: 数据库会话
            product_id: 商品ID
            user: 当前用户

        Raises:
            NotFoundError: 商品不存在
        """
        # 获取商品
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise NotFoundError("商品不存在")

        # 删除商品
        db.delete(product)
        db.commit()

