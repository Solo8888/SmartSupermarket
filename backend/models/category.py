# 商品类别模型
# 定义商品类别相关的数据库模型
from sqlalchemy import Column, Integer, String, Text, SmallInteger, Enum, ForeignKey, DateTime
from sqlalchemy.sql import func
from . import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True, comment='分类ID')
    name = Column(String(50), nullable=False, comment='分类名称')
    parent_id = Column(Integer, ForeignKey('categories.id', ondelete='SET NULL'), nullable=True, comment='父分类ID')
    description = Column(Text, nullable=True, comment='分类描述')
    level = Column(SmallInteger, default=1, nullable=False, comment='分类级别')
    sort_order = Column(Integer, default=0, nullable=False, comment='排序顺序')
    status = Column(Enum('active', 'inactive'), default='active', nullable=False, comment='状态')
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False, comment='更新时间')