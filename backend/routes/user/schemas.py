# 用户数据模型
# 定义用户相关的请求和响应数据模型

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    """用户角色枚举"""
    customer = "customer"
    operations_manager = "operations_manager"
    inventory_manager = "inventory_manager"
    system_admin = "system_admin"


class UserStatus(str, Enum):
    """用户状态枚举"""
    active = "active"
    inactive = "inactive"


class UserResponse(BaseModel):
    """用户响应模型"""
    id: str
    username: str
    phone: Optional[str] = None
    gender: Optional[str] = None
    role: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应模型"""
    items: list[UserResponse]
    total: int


class UserUpdateRole(BaseModel):
    """更新用户角色请求模型"""
    role: UserRole = Field(..., description="用户角色")