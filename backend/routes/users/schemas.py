# 用户模块数据模型
# 定义用户相关的请求和响应数据模型

from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


# 认证相关模型
class LoginRequest(BaseModel):
    """登录请求"""
    phone: str = Field(..., description="手机号")
    password: str = Field(..., description="密码")


class LoginResponse(BaseModel):
    """登录响应"""
    access_token: str
    token_type: str
    user_id: str
    username: str
    role: str


class RegisterRequest(BaseModel):
    """注册请求"""
    username: str = Field(..., description="用户名")
    phone: str = Field(..., description="手机号")
    password: str = Field(..., description="密码")
    role: str = Field(..., description="角色")


class RegisterResponse(BaseModel):
    """注册响应"""
    user_id: str
    username: str
    phone: str
    role: str


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., description="新密码")


class ChangePasswordResponse(BaseModel):
    """修改密码响应"""
    message: str


# 用户管理相关模型
class UserUpdateRole(BaseModel):
    """更新用户角色请求"""
    role: str = Field(..., description="新角色")


class UserResponse(BaseModel):
    """用户响应"""
    id: str
    username: str
    phone: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """用户列表响应"""
    items: List[UserResponse]
    total: int
    page: int
    size: int
