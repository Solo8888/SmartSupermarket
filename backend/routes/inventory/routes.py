

# 库存API路由
# 提供库存的增删改查接口

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import get_db, User
from core.permitions import require_role
from .schemas import InventoryResponse, InventoryUpdate, StockInRequest, StockOutRequest
from .service import InventoryService
from fastapi_pagination import Page, Params

inventory_router = APIRouter(prefix='/inventory', tags=['inventory'])


@inventory_router.get('/', response_model=Page[InventoryResponse])
async def get_inventories(
        params: Params = Depends(),
        db: Session = Depends(get_db)
):
    """
    获取库存列表接口

    Args:
        params: 分页参数
        db: 数据库会话

    Returns:
        库存列表（分页）
    """
    return InventoryService.get_inventories(db, params)

