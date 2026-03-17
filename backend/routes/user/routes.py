# 用户API路由
# 提供用户管理的接口

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import get_db, User
from core.permitions import require_role
from .schemas import UserResponse, UserListResponse, UserUpdateRole
from .service import UserService

user_router = APIRouter(prefix='/users', tags=['users'])


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