

# 库存服务
# 处理库存相关的业务逻辑

from sqlalchemy.orm import Session
from sqlalchemy import func
from models.inventory import Inventory
from models.product import Product
from .schemas import InventoryUpdate, StockInRequest, StockOutRequest
from core.exceptions import NotFoundError
from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate


class InventoryService:
    @staticmethod
    def get_inventories(db: Session, params: Params) -> Page[Inventory]:
        """
        获取库存列表

        Args:
            db: 数据库会话
            params: 分页参数

        Returns:
            库存列表（分页）
        """
        query = db.query(Inventory).order_by(Inventory.id.asc())
        return sqlalchemy_paginate(query, params=params)

    @staticmethod
    def get_inventory(db: Session, product_id: int) -> dict:
        """
        获取单个商品库存

        Args:
            db: 数据库会话
            product_id: 商品ID

        Returns:
            商品库存信息

        Raises:
            NotFoundError: 库存不存在
        """
        inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
        if not inventory:
            raise NotFoundError("库存不存在")

        return {
            "id": inventory.id,
            "product_id": inventory.product_id,
            "warehouse_id": inventory.warehouse_id,
            "stock_quantity": inventory.stock_quantity,
            "warning_quantity": inventory.warning_quantity,
            "last_stock_time": inventory.last_stock_time,
            "created_at": inventory.created_at,
            "updated_at": inventory.updated_at
        }

    @staticmethod
    def update_inventory(db: Session, product_id: int, payload: InventoryUpdate, user) -> dict:
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
        """
        inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
        if not inventory:
            raise NotFoundError("库存不存在")

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
            "warehouse_id": inventory.warehouse_id,
            "stock_quantity": inventory.stock_quantity,
            "warning_quantity": inventory.warning_quantity,
            "last_stock_time": inventory.last_stock_time,
            "created_at": inventory.created_at,
            "updated_at": inventory.updated_at
        }

    @staticmethod
    def stock_in(db: Session, product_id: int, payload: StockInRequest, user) -> dict:
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
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise NotFoundError("商品不存在")

        inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
        if not inventory:
            inventory = Inventory(
                product_id=product_id,
                stock_quantity=payload.quantity
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
            "warehouse_id": inventory.warehouse_id,
            "stock_quantity": inventory.stock_quantity,
            "warning_quantity": inventory.warning_quantity,
            "last_stock_time": inventory.last_stock_time,
            "created_at": inventory.created_at,
            "updated_at": inventory.updated_at
        }

    @staticmethod
    def stock_out(db: Session, product_id: int, payload: StockOutRequest, user) -> dict:
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
        """
        inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
        if not inventory:
            raise NotFoundError("库存不存在")

        if inventory.stock_quantity < payload.quantity:
            raise ValueError("库存不足")

        inventory.stock_quantity -= payload.quantity
        inventory.last_stock_time = func.current_timestamp()
        inventory.updated_at = func.current_timestamp()

        db.commit()
        db.refresh(inventory)

        return {
            "id": inventory.id,
            "product_id": inventory.product_id,
            "warehouse_id": inventory.warehouse_id,
            "stock_quantity": inventory.stock_quantity,
            "warning_quantity": inventory.warning_quantity,
            "last_stock_time": inventory.last_stock_time,
            "created_at": inventory.created_at,
            "updated_at": inventory.updated_at
        }

