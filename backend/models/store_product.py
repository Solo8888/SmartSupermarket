# 门店商品关联模型
# 定义门店与商品的关联关系
import uuid
from sqlalchemy import Column, String, Enum, ForeignKey, DateTime
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from . import Base


class StoreProduct(Base):
    __tablename__ = "store_products"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='ID')
    store_id = Column(CHAR(36), ForeignKey('stores.id', ondelete='CASCADE'), nullable=False, comment='门店ID')
    product_id = Column(CHAR(36), ForeignKey('products.id', ondelete='CASCADE'), nullable=False, comment='商品ID')
    status = Column(Enum('active', 'inactive'), default='active', nullable=False, comment='状态')
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False,
                        comment='更新时间')
