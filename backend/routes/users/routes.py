# 用户模块路由
# 处理用户认证和管理的API端点

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from models import get_db, User
from core.auth import get_current_user_id
from core.permitions import require_role

from .schemas import (
    LoginRequest, LoginResponse, RegisterRequest, RegisterResponse, 
    ChangePasswordRequest, ChangePasswordResponse, UserResponse, 
    UserListResponse, UserUpdateRole
)
from .service import AuthService, UserService

# 创建用户路由器
user_router = APIRouter(prefix='/users', tags=['users'])


# 认证相关路由
@user_router.post('/login', response_model=LoginResponse)
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


@user_router.post('/register', response_model=RegisterResponse)
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


@user_router.post('/change-password', response_model=ChangePasswordResponse)
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


# 用户管理相关路由
@user_router.get('/', response_model=UserListResponse)
async def get_user_list(
        user: User = Depends(require_role('system_admin', mode='eq')),
        db: Session = Depends(get_db)
):
    """
    获取用户列表接口

    Args:
        user: 当前用户
        db: 数据库会话

    Returns:
        用户列表
    """
    result = UserService.get_user_list(db, user)
    return UserListResponse(**result)


@user_router.put('/{user_id}/role', response_model=UserResponse)
async def update_user_role(
        user_id: str,
        payload: UserUpdateRole,
        user: User = Depends(require_role('system_admin', mode='eq')),
        db: Session = Depends(get_db)
):
    """
    更新用户角色接口

    Args:
        user_id: 用户ID
        payload: 更新用户角色请求体
        user: 当前用户
        db: 数据库会话

    Returns:
        更新后的用户信息
    """
    result = UserService.update_user_role(db, user_id, payload, user)
    return UserResponse(**result)
