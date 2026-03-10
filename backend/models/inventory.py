
# 库存模型
# 定义库存相关的数据库模型
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.sql import func
from . import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, autoincrement=True, comment='库存ID')
    product_id = Column(Integer, ForeignKey('products.id', ondelete='CASCADE'), nullable=False, unique=True, comment='商品ID')
    warehouse_id = Column(Integer, nullable=False, default=1, comment='仓库ID')
    stock_quantity = Column(Integer, nullable=False, default=0, comment='库存数量')
    warning_quantity = Column(Integer, nullable=False, default=10, comment='预警数量')
    last_stock_time = Column(DateTime, default=func.current_timestamp(), nullable=False, comment='最后库存更新时间')
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False,
                        comment='更新时间')

