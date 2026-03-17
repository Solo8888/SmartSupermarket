# 门店API路由
# 提供门店的增删改查接口

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import get_db, User
from core.permitions import require_role
from .schemas import StoreCreate, StoreUpdate, StoreResponse
from .service import StoreService
from fastapi_pagination import Page, Params
from typing import List

store_router = APIRouter(prefix='/stores', tags=['门店路由'])


@store_router.post('/', response_model=StoreResponse)
async def create_store(
        payload: StoreCreate,
        user: User = Depends(require_role('system_admin', mode='eq')),
        db: Session = Depends(get_db)
):
    """
    创建门店接口

    Args:
        payload: 创建门店请求体
        user: 当前用户
        db: 数据库会话

    Returns:
        创建成功的门店信息
    """
    store = StoreService.create_store(db, payload, user)
    return StoreResponse(**store)


@store_router.get('/', response_model=Page[StoreResponse])
async def get_stores(
        params: Params = Depends(),
        db: Session = Depends(get_db)
):
    """
    获取门店列表接口（分页）

    Args:
        params: 分页参数
        db: 数据库会话

    Returns:
        门店列表（分页）
    """
    return StoreService.get_stores(db, params)


@store_router.get('/all', response_model=List[StoreResponse])
async def get_all_stores(
        db: Session = Depends(get_db)
):
    """
    获取所有门店接口（不分页）

    Args:
        db: 数据库会话

    Returns:
        所有门店列表
    """
    stores = StoreService.get_all_stores(db)
    return [StoreResponse(**store) for store in stores]


@store_router.get('/{store_id}', response_model=StoreResponse)
async def get_store(
        store_id: str,
        db: Session = Depends(get_db)
):
    """
    获取单个门店详情接口

    Args:
        store_id: 门店ID
        db: 数据库会话

    Returns:
        门店详情
    """
    store = StoreService.get_store(db, store_id)
    return StoreResponse(**store)


@store_router.put('/{store_id}', response_model=StoreResponse)
async def update_store(
        store_id: str,
        payload: StoreUpdate,
        user: User = Depends(require_role('system_admin', mode='eq')),
        db: Session = Depends(get_db)
):
    """
    更新门店接口

    Args:
        store_id: 门店ID
        payload: 更新门店请求体
        user: 当前用户
        db: 数据库会话

    Returns:
        更新成功的门店信息
    """
    store = StoreService.update_store(db, store_id, payload, user)
    return StoreResponse(**store)
