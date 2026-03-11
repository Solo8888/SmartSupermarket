# 促销活动模型
# 定义促销活动相关的数据库模型
import uuid
from sqlalchemy import Column, Integer, String, Text, SmallInteger, Enum, ForeignKey, DateTime, Numeric
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from . import Base


class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='促销活动ID')
    name = Column(String(100), nullable=False, comment='促销活动名称')
    description = Column(Text, nullable=True, comment='促销活动描述')
    type = Column(Enum('discount', 'special_price', 'buy_x_get_y', 'bundle'), nullable=False, comment='促销类型')
    value = Column(Numeric(10, 2), nullable=False, comment='促销值（折扣率或减价金额）')
    start_time = Column(DateTime, nullable=False, comment='开始时间')
    end_time = Column(DateTime, nullable=False, comment='结束时间')
    status = Column(Enum('draft', 'active', 'paused', 'ended'), default='draft', nullable=False, comment='状态')
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False,
                        comment='更新时间')
