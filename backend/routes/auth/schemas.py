# 认证模块数据模型
# 手机号登录和注册请求数据模型

from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    phone: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = 'bearer'
    user_id: int
    phone: str
    name: Optional[str] = None


class RegisterRequest(BaseModel):
    username: str
    phone: str
    password: str
    role: str = 'customer'


class RegisterResponse(BaseModel):
    user_id: int
    username: str
    phone: str
    role: str
    message: str = '注册成功'
