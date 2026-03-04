# 认证路由模块
# 处理手机号登录和注册API端点
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from passlib.context import CryptContext
from models import get_db

from .schemas import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse
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


@auth_router.post('/register', response_model=RegisterResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    新用户注册接口

    Args:
        request: 注册请求体，包含用户名、手机号、密码和角色
        db: 数据库会话

    Returns:
        注册成功后的响应
    """
    auth_service = AuthService()
    result = auth_service.register(db, request.username, request.phone, request.password, request.role)
    return RegisterResponse(**result)
