# 会员模型
# 定义会员相关的数据库模型
import uuid
from sqlalchemy import Column, String, Date, DateTime, ForeignKey
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from . import Base


class Member(Base):
    __tablename__ = "members"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='会员ID')
    user_id = Column(CHAR(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment='用户ID')
    name = Column(String(50), nullable=False, comment='会员姓名')
    birthday = Column(Date, nullable=True, comment='生日')
    member_level_id = Column(CHAR(36), ForeignKey('member_levels.id', ondelete='CASCADE'), nullable=False, comment='会员等级ID')
    expire_date = Column(DateTime, nullable=False, comment='会员到期时间')
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False,
                        comment='更新时间')
