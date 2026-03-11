# 订单API路由
# 提供订单的增删改查接口

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from models import get_db, User
from core.permitions import require_role
from .schemas import OrderCreate, OrderResponse, OrderPay, OrderUpdateStatus
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
        user: User = Depends(require_role('customer')),
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
        user: User = Depends(require_role('customer')),
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


@order_router.post('/{order_id}/pay', response_model=OrderResponse)
async def pay_order(
        order_id: str,
        payload: OrderPay,
        user: User = Depends(require_role('customer')),
        db: Session = Depends(get_db)
):
    """
    支付订单接口

    Args:
        order_id: 订单ID
        payload: 支付请求体
        user: 当前用户
        db: 数据库会话

    Returns:
        支付成功的订单信息
    """
    order = OrderService.pay_order(db, order_id, payload.payment_method, user)
    return OrderResponse(**order)


@order_router.put('/{order_id}/status', response_model=OrderResponse)
async def update_order_status(
        order_id: str,
        payload: OrderUpdateStatus,
        user: User = Depends(require_role(['inventory_manager', 'operations_manager'], mode='in')),
        db: Session = Depends(get_db)
):
    """
    更新订单状态接口

    Args:
        order_id: 订单ID
        payload: 更新订单状态请求体
        user: 当前用户
        db: 数据库会话

    Returns:
        更新后的订单信息
    """
    order = OrderService.update_order_status(db, order_id, payload.status, user)
    return OrderResponse(**order)


@order_router.post('/{order_id}/cancel', response_model=OrderResponse)
async def cancel_order(
        order_id: str,
        user: User = Depends(require_role('customer')),
        db: Session = Depends(get_db)
):
    """
    取消订单接口

    Args:
        order_id: 订单ID
        user: 当前用户
        db: 数据库会话

    Returns:
        取消后的订单信息
    """
    order = OrderService.cancel_order(db, order_id, user)
    return OrderResponse(**order)
