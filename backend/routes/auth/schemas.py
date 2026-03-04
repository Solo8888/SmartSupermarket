# 认证模块数据模型
# 手机号登录请求数据模型

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
