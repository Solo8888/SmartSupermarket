# 会员等级模型
# 定义会员等级相关的数据库模型
import uuid
from sqlalchemy import Column, String, Enum, Numeric, DateTime
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from . import Base


class MemberLevel(Base):
    __tablename__ = "member_levels"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='会员等级ID')
    name = Column(String(20), nullable=False, comment='等级名称')
    level = Column(Enum('level1', 'level2'), nullable=False, unique=True, comment='等级标识')
    discount = Column(Numeric(5, 2), nullable=False, comment='固定折扣')
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False,
                        comment='更新时间')
