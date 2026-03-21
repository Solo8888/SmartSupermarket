# 用户-门店关联模型
# 定义用户和门店之间的关联关系
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func

from . import Base


class UserStore(Base):
    __tablename__ = "user_store"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='ID')
    user_id = Column(CHAR(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, comment='用户ID')
    store_id = Column(CHAR(36), ForeignKey('stores.id', ondelete='CASCADE'), nullable=False, comment='门店ID')
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False, comment='创建时间')

    # 添加唯一约束，确保一个用户在一个门店只能有一条记录
    __table_args__ = (
        UniqueConstraint('user_id', 'store_id', name='user_store_user_id_store_id_uindex'),
    )
