# 购物车模型
# 定义购物车相关的数据库模型
import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Numeric
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from . import Base


class Cart(Base):
    __tablename__ = "carts"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()),
                comment='购物车ID')
    user_id = Column(CHAR(36), ForeignKey('users.id', ondelete='CASCADE'),
                     nullable=False, comment='用户ID')
    created_at = Column(DateTime, default=func.current_timestamp(),
                        nullable=False, comment='创建时间')
    updated_at = Column(
        DateTime, default=func.current_timestamp(),
        onupdate=func.current_timestamp(), nullable=False,
        comment='更新时间'
    )


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()),
                comment='购物车项ID')
    cart_id = Column(CHAR(36), ForeignKey('carts.id', ondelete='CASCADE'),
                     nullable=False, comment='购物车ID')
    product_id = Column(
        CHAR(36), ForeignKey('products.id', ondelete='SET NULL'),
        nullable=True, comment='商品ID'
    )
    product_name = Column(String(100), nullable=False, comment='商品名称')
    product_image = Column(String(255), nullable=True, comment='商品图片')
    price = Column(Numeric(10, 2), nullable=False, comment='商品单价')
    quantity = Column(Integer, nullable=False, comment='购买数量')
    created_at = Column(DateTime, default=func.current_timestamp(),
                        nullable=False, comment='创建时间')
    updated_at = Column(
        DateTime, default=func.current_timestamp(),
        onupdate=func.current_timestamp(), nullable=False,
        comment='更新时间'
    )
