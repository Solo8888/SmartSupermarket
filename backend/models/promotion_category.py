# 促销活动分类关联模型
# 定义促销活动与分类关联相关的数据库模型
import uuid
from sqlalchemy import Column, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from . import Base


class PromotionCategory(Base):
    __tablename__ = "promotion_categories"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='ID')
    promotion_id = Column(CHAR(36), ForeignKey('promotions.id', ondelete='CASCADE'), nullable=False, comment='促销活动ID')
    category_id = Column(CHAR(36), ForeignKey('categories.id', ondelete='CASCADE'), nullable=False, comment='商品类别ID')
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False, comment='创建时间')
