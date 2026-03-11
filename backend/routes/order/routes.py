# 订单API路由
# 提供订单的增删改查接口

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import get_db, User
from core.permitions import require_role
from .schemas import OrderCreate, OrderResponse
from .service import OrderService

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
