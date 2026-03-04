# 用户模型
# 定义用户相关的数据库模型
from sqlalchemy import Column, Integer, String, DateTime, Enum
from . import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String)
    password = Column(String)
    phone = Column(String)
    role = Column(Enum('customer', 'operations_manager', 'inventory_manager', name='user_roles', default='customer'))
    status = Column(Enum('active', 'inactive', name='user_status', default='active'))
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
