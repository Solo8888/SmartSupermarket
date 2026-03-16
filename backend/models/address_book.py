# 地址簿模型
# 定义地址簿相关的数据库模型
import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from . import Base


class AddressBook(Base):
    __tablename__ = "address_book"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='地址ID')
    user_id = Column(CHAR(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment='用户ID')
    recipient = Column(String(50), nullable=False, comment='收货人姓名')
    phone = Column(String(20), nullable=False, comment='联系电话')
    province = Column(String(50), nullable=False, comment='省份')
    city = Column(String(50), nullable=False, comment='城市')
    district = Column(String(50), nullable=False, comment='区县')
    detail_address = Column(Text, nullable=False, comment='详细地址')
    is_default = Column(Boolean, nullable=False, default=False, comment='是否默认地址')
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False,
                        comment='更新时间')
