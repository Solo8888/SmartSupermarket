# 门店模型
# 定义门店相关的数据库模型
import uuid
from sqlalchemy import Column, String, Text, Enum, DateTime
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from . import Base


class Store(Base):
    __tablename__ = "stores"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='门店ID')
    name = Column(String(100), nullable=False, comment='门店名称')
    address = Column(Text, nullable=False, comment='门店地址')
    phone = Column(String(20), nullable=False, comment='联系电话')
    opening_hours = Column(String(100), nullable=False, comment='营业时间')
    status = Column(Enum('active', 'inactive'), nullable=False, comment='门店状态')
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False,
                        comment='更新时间')
