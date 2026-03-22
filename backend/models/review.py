# 评价模型
# 定义评价相关的数据库模型
import uuid
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Numeric
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from . import Base


class Review(Base):
    __tablename__ = "reviews"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='评价ID')
    order_id = Column(CHAR(36), ForeignKey('orders.id', ondelete='CASCADE'), nullable=False, comment='订单ID')
    order_item_id = Column(CHAR(36), ForeignKey('order_items.id', ondelete='CASCADE'), nullable=False, comment='订单项ID')
    user_id = Column(CHAR(36), ForeignKey('users.id', ondelete='SET NULL'), nullable=True, comment='用户ID')
    product_id = Column(CHAR(36), ForeignKey('products.id', ondelete='SET NULL'), nullable=True, comment='商品ID')
    rating = Column(Integer, nullable=False, comment='评分（1-5星）')
    content = Column(Text, nullable=True, comment='评价内容')
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False, comment='创建时间')
