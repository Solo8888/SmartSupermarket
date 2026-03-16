# 折扣券模型
# 定义折扣券相关的数据库模型
import uuid
from sqlalchemy import Column, String, Text, Enum, Numeric, DateTime
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from . import Base


class Coupon(Base):
    __tablename__ = "coupons"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='折扣券ID')
    name = Column(String(100), nullable=False, comment='折扣券名称')
    description = Column(Text, nullable=True, comment='折扣券描述')
    type = Column(Enum('fixed'), nullable=False, comment='折扣券类型')
    value = Column(Numeric(10, 2), nullable=False, comment='折扣值')
    min_spend = Column(Numeric(10, 2), nullable=False, comment='最低消费金额')
    start_time = Column(DateTime, nullable=False, comment='有效期开始时间')
    end_time = Column(DateTime, nullable=False, comment='有效期结束时间')
    status = Column(Enum('active', 'inactive'), nullable=False, comment='状态')
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False,
                        comment='更新时间')
