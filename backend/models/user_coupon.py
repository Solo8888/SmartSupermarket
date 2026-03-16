# 用户折扣券模型
# 定义用户-折扣券关联相关的数据库模型
import uuid
from sqlalchemy import Column, Enum, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from . import Base


class UserCoupon(Base):
    __tablename__ = "user_coupons"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='ID')
    user_id = Column(CHAR(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment='用户ID')
    coupon_id = Column(CHAR(36), ForeignKey('coupons.id', ondelete='CASCADE'), nullable=False, comment='折扣券ID')
    status = Column(Enum('unused', 'used', 'expired'), nullable=False, comment='状态')
    acquired_at = Column(DateTime, nullable=False, comment='领取时间')
    used_at = Column(DateTime, nullable=True, comment='使用时间')
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False, comment='创建时间')
