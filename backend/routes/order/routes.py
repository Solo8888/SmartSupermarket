# 订单API路由
# 提供订单的增删改查接口

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from models import get_db, User
from core.permitions import require_role
from .schemas import OrderCreate, OrderResponse
from .service import OrderService
from fastapi_pagination import Page, Params
from typing import Optional

order_router = APIRouter(prefix='/orders', tags=['orders'])


@order_router.post('/', response_model=OrderResponse)
async def create_order(
        payload: OrderCreate,
        user: User = Depends(require_role('customer')),
        db: Session = Depends(get_db)
):
    """
    创建订单接口

    Args:
        payload: 创建订单请求体
        user: 当前用户
        db: 数据库会话

    Returns:
        创建成功的订单信息
    """
    order = OrderService.create_order(db, payload, user)
    return OrderResponse(**order)


@order_router.get('/', response_model=Page[OrderResponse])
async def get_orders(
        params: Params = Depends(),
        status: Optional[str] = Query(None, description="订单状态筛选"),
        user: User = Depends(require_role(['customer', 'inventory_manager', 'operations_manager'], mode='in')),
        db: Session = Depends(get_db)
):
    """
    获取订单列表接口（分页）

    Args:
        params: 分页参数
        status: 订单状态筛选（可选）
        user: 当前用户
        db: 数据库会话

    Returns:
        订单列表（分页）
    """
    return OrderService.get_orders(db, params, user, status)


@order_router.get('/{order_id}', response_model=OrderResponse)
async def get_order(
        order_id: str,
        user: User = Depends(require_role(['customer', 'inventory_manager', 'operations_manager'], mode='in')),
        db: Session = Depends(get_db)
):
    """
    获取订单详情接口

    Args:
        order_id: 订单ID
        user: 当前用户
        db: 数据库会话

    Returns:
        订单详情（包含订单项）
    """
    order = OrderService.get_order(db, order_id, user)
    return OrderResponse(**order)
