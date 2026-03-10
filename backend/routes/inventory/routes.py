

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


@inventory_router.get('/{product_id}', response_model=InventoryResponse)
async def get_inventory(
        product_id: int,
        db: Session = Depends(get_db)
):
    """
    获取单个商品库存接口

    Args:
        product_id: 商品ID
        db: 数据库会话

    Returns:
        商品库存信息
    """
    inventory = InventoryService.get_inventory(db, product_id)
    return InventoryResponse(**inventory)


@inventory_router.put('/{product_id}', response_model=InventoryResponse)
async def update_inventory(
        product_id: int,
        payload: InventoryUpdate,
        user: User = Depends(require_role('inventory_manager')),
        db: Session = Depends(get_db)
):
    """
    更新库存接口

    Args:
        product_id: 商品ID
        payload: 更新库存请求体
        user: 当前用户
        db: 数据库会话

    Returns:
        更新成功的库存信息
    """
    inventory = InventoryService.update_inventory(db, product_id, payload, user)
    return InventoryResponse(**inventory)

