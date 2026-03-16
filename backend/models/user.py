# 用户模型
# 定义用户相关的数据库模型
import uuid
from sqlalchemy import Column, String, DateTime, Enum
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.sql import func
from . import Base


class User(Base):
    __tablename__ = "users"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment='用户ID')
    username = Column(String(50), nullable=False, unique=True, comment='用户名')
    password = Column(String(255), nullable=False, comment='密码')
    phone = Column(String(20), nullable=True, comment='手机号')
    gender = Column(Enum('male', 'female'), nullable=True, comment='性别')
    role = Column(Enum('customer', 'operations_manager', 'inventory_manager', 'system_admin', name='user_roles', default='customer'), nullable=False, comment='用户角色')
    status = Column(Enum('active', 'inactive', name='user_status', default='active'), nullable=False, comment='用户状态')
    created_at = Column(DateTime, default=func.current_timestamp(), nullable=False, comment='创建时间')
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp(), nullable=False, comment='更新时间')
