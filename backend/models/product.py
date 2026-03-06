# 商品模型
# 定义商品相关的数据库模型
from sqlalchemy import Column, Integer, String, Text, DECIMAL, Enum, ForeignKey, DateTime
from sqlalchemy.sql import func
from . import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True, comment='商品ID')
    name = Column(String(100), nullable=False, comment='商品名称')
    category_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'), nullable=False, comment='分类ID')
    price = Column(DECIMAL(10, 2), nullable=False, comment='商品价格')
    original_price = Column(DECIMAL(10, 2), nullable=True, comment='原价')
    description = Column(Text, nullable=True, comment='商品描述')
    image_url = Column(String(255), nullable=True, comment='商品图片URL')
    barcode = Column(String(50), nullable=True, unique=True, comment='商品条码')
    brand = Column(String(50), nullable=True, comment='品牌')
    unit = Column(String(20), nullable=False, default='个', comment='单位')
    status = Column(Enum('active', 'inactive', 'out_of_stock'), default='active', nullable=False, comment='状态')
    sales_count = Column(Integer, default=0, nullable=False, comment='销量')
    view_count = Column(Integer, default=0, nullable=False, comment='浏览量')
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False,
                        comment='更新时间')
