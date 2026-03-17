# 门店分配API路由
# 提供门店分配的增删改查接口

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import get_db, User
from core.permitions import require_role
from .schemas import StoreAllocationCreate, StoreAllocationResponse
from .service import UserStoreService

user_store_router = APIRouter(prefix='/user-store', tags=['user-store'])


@user_store_router.post('/', response_model=StoreAllocationResponse)
async def create_store_allocation(
        payload: StoreAllocationCreate,
        user: User = Depends(require_role('system_admin', mode='eq')),
        db: Session = Depends(get_db)
):
    """
    分配门店给用户接口

    Args:
        payload: 创建门店分配请求体
        user: 当前用户
        db: 数据库会话

    Returns:
        创建成功的门店分配信息
    """
    allocation = UserStoreService.create_store_allocation(db, payload, user)
    return StoreAllocationResponse(**allocation)
