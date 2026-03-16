# 促销活动商品关联模型
# 定义促销活动与商品关联相关的数据库模型
import uuid
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from . import Base


class PromotionProduct(Base):
    __tablename__ = "promotion_products"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='ID')
    promotion_id = Column(CHAR(36), ForeignKey('promotions.id', ondelete='CASCADE'), nullable=False, comment='促销活动ID')
    product_id = Column(CHAR(36), ForeignKey('products.id', ondelete='CASCADE'), nullable=False, comment='商品ID')
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False, comment='创建时间')
