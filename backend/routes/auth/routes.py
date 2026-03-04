# 认证路由模块
# 处理手机号登录API端点
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from passlib.context import CryptContext
from models import get_db

from .schemas import LoginRequest, LoginResponse
from .service import AuthService

# 创建认证路由器
auth_router = APIRouter(prefix='/users', tags=['authentication'])


@auth_router.post('/login', response_model=LoginResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    手机号登录接口

    Args:
        request: 登录请求体，包含手机号和密码
        db: 数据库会话

    Returns:
        登录成功后的响应
    """
    auth_service = AuthService()
    result = auth_service.login(db, request.phone, request.password)
    return LoginResponse(**result)
