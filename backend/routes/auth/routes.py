# 认证路由模块
# 处理手机号登录和注册API端点
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from passlib.context import CryptContext
from models import get_db

from .schemas import LoginRequest, LoginResponse, RegisterRequest, RegisterResponse, ChangePasswordRequest, ChangePasswordResponse
from .service import AuthService
from core.auth import get_current_user_id

# 创建认证路由器
auth_router = APIRouter(prefix='/users', tags=['认证路由'])


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


@auth_router.post('/change-password', response_model=ChangePasswordResponse)
async def change_password(
    request: ChangePasswordRequest, 
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    修改用户密码接口

    Args:
        request: 修改密码请求体，包含旧密码和新密码
        db: 数据库会话
        current_user_id: 当前登录用户ID

    Returns:
        修改密码成功后的响应
    """
    auth_service = AuthService()
    result = auth_service.change_password(db, current_user_id, request.old_password, request.new_password)
    return ChangePasswordResponse(**result)
