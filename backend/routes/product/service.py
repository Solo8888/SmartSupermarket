
# 商品服务
# 处理商品相关的业务逻辑

from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from models.product import Product
from models.category import Category
from models.user_store import UserStore
from models.inventory import Inventory
from .schemas import ProductCreate, ProductUpdate
from core.exceptions import NotFoundError, ClientError
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate


class ProductService:
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
        if payload.barcode and payload.barcode.strip():
            existing_product = db.query(Product).filter(Product.barcode == payload.barcode).first()
            if existing_product:
                raise ValueError("商品条码已存在")

        # 获取用户关联的门店ID
        user_store = db.query(UserStore).filter(UserStore.user_id == user.id).first()
        if not user_store:
            raise ValueError("用户未分配门店")
        store_id = user_store.store_id

        # 创建新商品
        product = Product(
            name=payload.name,
            category_id=payload.category_id,
            store_id=store_id,
            price=payload.price,
            original_price=payload.original_price,
            purchase_price=payload.purchase_price,
            description=payload.description,
            image_url=payload.image_url,
            barcode=payload.barcode.strip() if payload.barcode and payload.barcode.strip() else None,
            brand=payload.brand,
            origin=payload.origin,
            shelf_life=payload.shelf_life,
            unit=payload.unit,
            status=payload.status
        )

        db.add(product)
        db.commit()
        db.refresh(product)

        # 自动创建库存记录，默认库存为0
        from models.inventory import Inventory
        inventory = Inventory(
            product_id=product.id,
            stock_quantity=0,
            warning_quantity=10
        )
        db.add(inventory)
        db.commit()

        # 转换为字典返回
        return {
            "id": product.id,
            "name": product.name,
            "category_id": product.category_id,
            "store_id": product.store_id,
            "price": product.price,
            "original_price": product.original_price,
            "purchase_price": product.purchase_price,
            "description": product.description,
            "image_url": product.image_url,
            "barcode": product.barcode,
            "brand": product.brand,
            "origin": product.origin,
            "shelf_life": product.shelf_life,
            "unit": product.unit,
            "status": product.status,
            "sales_count": product.sales_count,
            "view_count": product.view_count,
            "created_at": product.created_at,
            "updated_at": product.updated_at
        }

    @staticmethod
    def get_products(db: Session, params: Params, search: str = None, store_id: str = None, user = None):
        """
        获取商品列表

        Args:
            db: 数据库会话
            params: 分页参数
            search: 搜索关键词（可选）
            store_id: 门店ID（可选），按门店过滤商品
            user: 当前用户

        Returns:
            商品列表（分页）
        """
        # 构建查询，关联库存表
        query = db.query(Product, Inventory.stock_quantity).outerjoin(Inventory, Product.id == Inventory.product_id).order_by(Product.id.asc())
        
        # 系统管理员和顾客可以查看所有商品，其他用户只能查看关联门店的商品
        if user and user.role not in ['system_admin', 'customer']:
            user_store_ids = ProductService.get_user_stores(db, user.id)
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
        
        # 门店过滤
        if store_id:
            query = query.filter(Product.store_id == store_id)
        
        # 执行查询
        result = sqlalchemy_paginate(query, params=params)
        
        # 处理结果，添加库存信息
        items = []
        for product, stock_quantity in result.items:
            product_dict = {
                "id": product.id,
                "name": product.name,
                "category_id": product.category_id,
                "store_id": product.store_id,
                "price": product.price,
                "original_price": product.original_price,
                "purchase_price": product.purchase_price,
                "description": product.description,
                "image_url": product.image_url,
                "barcode": product.barcode,
                "brand": product.brand,
                "origin": product.origin,
                "shelf_life": product.shelf_life,
                "unit": product.unit,
                "status": product.status,
                "sales_count": product.sales_count,
                "view_count": product.view_count,
                "stock": stock_quantity or 0,
                "created_at": product.created_at,
                "updated_at": product.updated_at
            }
            items.append(product_dict)
        
        # 返回修改后的分页结果
        return {
            "items": items,
            "total": result.total,
            "page": result.page,
            "size": result.size,
            "pages": result.pages
        }
    
    @staticmethod
    def get_all_products(db: Session, user = None) -> list:
        """
        获取所有商品（不分页）

        Args:
            db: 数据库会话
            user: 当前用户

        Returns:
            所有商品列表
        """
        # 构建查询，关联库存表
        query = db.query(Product, Inventory.stock_quantity).outerjoin(Inventory, Product.id == Inventory.product_id).order_by(Product.id.asc())
        
        # 系统管理员和顾客可以查看所有商品，其他用户只能查看关联门店的商品
        if user and user.role not in ['system_admin', 'customer']:
            user_store_ids = ProductService.get_user_stores(db, user.id)
            if user_store_ids:
                query = query.filter(Product.store_id.in_(user_store_ids))
            else:
                # 如果用户没有关联门店，返回空列表
                query = query.filter(Product.store_id.in_([]))
        
        results = query.all()
        return [
            {
                "id": product.id,
                "name": product.name,
                "category_id": product.category_id,
                "store_id": product.store_id,
                "price": product.price,
                "original_price": product.original_price,
                "purchase_price": product.purchase_price,
                "description": product.description,
                "image_url": product.image_url,
                "barcode": product.barcode,
                "brand": product.brand,
                "origin": product.origin,
                "shelf_life": product.shelf_life,
                "unit": product.unit,
                "status": product.status,
                "sales_count": product.sales_count,
                "view_count": product.view_count,
                "stock": stock_quantity or 0,
                "created_at": product.created_at,
                "updated_at": product.updated_at
            }
            for product, stock_quantity in results
        ]

    @staticmethod
    def get_product(db: Session, product_id: str, user = None) -> dict:
        """
        获取单个商品详情

        Args:
            db: 数据库会话
            product_id: 商品ID
            user: 当前用户

        Returns:
            商品详情

        Raises:
            NotFoundError: 商品不存在
            ClientError: 权限不足
        """
        # 获取商品和库存信息
        result = db.query(Product, Inventory.stock_quantity).outerjoin(Inventory, Product.id == Inventory.product_id).filter(Product.id == product_id).first()
        if not result:
            raise NotFoundError("商品不存在")
        
        product, stock_quantity = result

        # 系统管理员和顾客可以查看所有商品，其他用户只能查看关联门店的商品
        if user and user.role not in ['system_admin', 'customer']:
            user_store_ids = ProductService.get_user_stores(db, user.id)
            if product.store_id not in user_store_ids:
                raise ClientError("权限不足，无法查看此商品", "PERMISSION_DENIED")

        return {
            "id": product.id,
            "name": product.name,
            "category_id": product.category_id,
            "store_id": product.store_id,
            "price": product.price,
            "original_price": product.original_price,
            "purchase_price": product.purchase_price,
            "description": product.description,
            "image_url": product.image_url,
            "barcode": product.barcode,
            "brand": product.brand,
            "origin": product.origin,
            "shelf_life": product.shelf_life,
            "unit": product.unit,
            "status": product.status,
            "sales_count": product.sales_count,
            "view_count": product.view_count,
            "stock": stock_quantity or 0,
            "created_at": product.created_at,
            "updated_at": product.updated_at
        }

    @staticmethod
    def update_product(db: Session, product_id: str, payload: ProductUpdate, user) -> dict:
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
            ClientError: 权限不足
        """
        # 获取商品
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise NotFoundError("商品不存在")

        # 系统管理员可以更新所有商品，其他用户只能更新关联门店的商品
        if user.role != 'system_admin':
            user_store_ids = ProductService.get_user_stores(db, user.id)
            if product.store_id not in user_store_ids:
                raise ClientError("权限不足，无法更新此商品", "PERMISSION_DENIED")

        # 检查分类是否存在（如果提供了category_id）
        if payload.category_id is not None:
            category = db.query(Category).filter(Category.id == payload.category_id).first()
            if not category:
                raise ValueError("分类不存在")

        # 检查条码是否已存在（如果提供了barcode且不是当前商品的barcode）
        if payload.barcode is not None and payload.barcode.strip():
            existing_product = db.query(Product).filter(Product.barcode == payload.barcode).filter(Product.id != product_id).first()
            if existing_product:
                raise ValueError("商品条码已存在")

        # 更新字段（只更新提供的字段）
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if field == 'barcode' and value and value.strip():
                setattr(product, field, value.strip())
            elif field == 'barcode' and (not value or not value.strip()):
                setattr(product, field, None)
            else:
                setattr(product, field, value)

        # 更新时间戳
        product.updated_at = func.current_timestamp()

        db.commit()
        db.refresh(product)

        return {
            "id": product.id,
            "name": product.name,
            "category_id": product.category_id,
            "store_id": product.store_id,
            "price": product.price,
            "original_price": product.original_price,
            "purchase_price": product.purchase_price,
            "description": product.description,
            "image_url": product.image_url,
            "barcode": product.barcode,
            "brand": product.brand,
            "origin": product.origin,
            "shelf_life": product.shelf_life,
            "unit": product.unit,
            "status": product.status,
            "sales_count": product.sales_count,
            "view_count": product.view_count,
            "created_at": product.created_at,
            "updated_at": product.updated_at
        }

    @staticmethod
    def delete_product(db: Session, product_id: str, user) -> None:
        """
        删除商品

        Args:
            db: 数据库会话
            product_id: 商品ID
            user: 当前用户

        Raises:
            NotFoundError: 商品不存在
            ClientError: 权限不足
        """
        # 获取商品
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise NotFoundError("商品不存在")

        # 系统管理员可以删除所有商品，其他用户只能删除关联门店的商品
        if user.role != 'system_admin':
            user_store_ids = ProductService.get_user_stores(db, user.id)
            if product.store_id not in user_store_ids:
                raise ClientError("权限不足，无法删除此商品", "PERMISSION_DENIED")

        # 删除商品
        db.delete(product)
        db.commit()

    @staticmethod
    def get_products_by_category(db: Session, category_id: str, store_id: str = None, user = None) -> list:
        """
        按分类获取商品

        Args:
            db: 数据库会话
            category_id: 分类ID
            store_id: 门店ID（可选），按门店过滤商品
            user: 当前用户

        Returns:
            该分类下的商品列表
        """
        # 构建查询，关联库存表
        query = db.query(Product, Inventory.stock_quantity).outerjoin(Inventory, Product.id == Inventory.product_id).filter(
            Product.category_id == category_id,
            Product.status == 'active'
        )
        
        # 系统管理员和顾客可以查看所有商品，其他用户只能查看关联门店的商品
        if user and user.role not in ['system_admin', 'customer']:
            user_store_ids = ProductService.get_user_stores(db, user.id)
            if user_store_ids:
                query = query.filter(Product.store_id.in_(user_store_ids))
            else:
                # 如果用户没有关联门店，返回空列表
                query = query.filter(Product.store_id.in_([]))
        
        # 门店过滤
        if store_id:
            query = query.filter(Product.store_id == store_id)
        
        results = query.all()
        return [
            {
                "id": product.id,
                "name": product.name,
                "category_id": product.category_id,
                "store_id": product.store_id,
                "price": product.price,
                "image_url": product.image_url,
                "stock": stock_quantity or 0
            }
            for product, stock_quantity in results
        ]

