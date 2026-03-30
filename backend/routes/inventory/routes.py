

# 库存API路由
# 提供库存的增删改查接口

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import get_db, User
from core.permitions import require_role
from .schemas import InventoryResponse, InventoryUpdate, StockInRequest, StockOutRequest, ReplenishmentResponse, TransferPlansResponse, ThresholdUpdateRequest, ThresholdUpdateResponse
from .service import InventoryService
from fastapi_pagination import Page, Params

inventory_router = APIRouter(prefix='/inventory', tags=['inventory'])


@inventory_router.get('', response_model=Page[InventoryResponse])
async def get_inventories(
        params: Params = Depends(),
        search: str = None,
        user: User = Depends(require_role('inventory_manager')),
        db: Session = Depends(get_db)
):
    """
    获取库存列表接口

    Args:
        params: 分页参数
        search: 搜索关键词（可选），支持搜索商品名称、品牌、条码
        user: 当前用户
        db: 数据库会话

    Returns:
        库存列表（分页）
    """
    return InventoryService.get_inventories(db, params, search, user)


@inventory_router.get('/{product_id}', response_model=InventoryResponse)
async def get_inventory(
        product_id: str,
        user: User = Depends(require_role('inventory_manager')),
        db: Session = Depends(get_db)
):
    """
    获取单个商品库存接口

    Args:
        product_id: 商品ID
        user: 当前用户
        db: 数据库会话

    Returns:
        商品库存信息
    """
    inventory = InventoryService.get_inventory(db, product_id, user)
    return InventoryResponse(**inventory)


@inventory_router.put('/{product_id}', response_model=InventoryResponse)
async def update_inventory(
        product_id: str,
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


@inventory_router.post('/stock-in/{product_id}', response_model=InventoryResponse)
async def stock_in(
        product_id: str,
        payload: StockInRequest,
        user: User = Depends(require_role('inventory_manager')),
        db: Session = Depends(get_db)
):
    """
    入库登记接口

    Args:
        product_id: 商品ID
        payload: 入库请求体
        user: 当前用户
        db: 数据库会话

    Returns:
        更新后的库存信息
    """
    inventory = InventoryService.stock_in(db, product_id, payload, user)
    return InventoryResponse(**inventory)


@inventory_router.post('/stock-out/{product_id}', response_model=InventoryResponse)
async def stock_out(
        product_id: str,
        payload: StockOutRequest,
        user: User = Depends(require_role('inventory_manager')),
        db: Session = Depends(get_db)
):
    """
    出库审核接口

    Args:
        product_id: 商品ID
        payload: 出库请求体
        user: 当前用户
        db: 数据库会话

    Returns:
        更新后的库存信息
    """
    inventory = InventoryService.stock_out(db, product_id, payload, user)
    return InventoryResponse(**inventory)


@inventory_router.get('/optimization/replenishment', response_model=ReplenishmentResponse)
async def get_replenishment_suggestions(
        store_id: str = None,
        category_id: str = None,
        user: User = Depends(require_role('inventory_manager')),
        db: Session = Depends(get_db)
):
    """
    获取补货建议接口

    根据当前库存和安全库存计算建议补货量。
    计算公式：suggested_replenishment = max(0, safety_stock * 2 - current_stock)

    Args:
        store_id: 仓库ID（可选），用于筛选特定仓库的补货建议
        category_id: 商品类别ID（可选），用于筛选特定类别的补货建议
        user: 当前用户
        db: 数据库会话

    Returns:
        补货建议列表
    """
    suggestions = InventoryService.get_replenishment_suggestions(db, store_id, category_id, user)
    return ReplenishmentResponse(suggestions=suggestions)


@inventory_router.get('/optimization/transfer', response_model=TransferPlansResponse)
async def get_transfer_plans(
        product_id: str = None,
        user: User = Depends(require_role('inventory_manager')),
        db: Session = Depends(get_db)
):
    """
    获取库存调拨方案接口

    分析各门店的库存状况，识别库存不平衡的商品，生成库存调拨方案。

    算法逻辑：
    1. 识别库存不平衡：计算每个商品在各门店的库存标准差
    2. 确定调出门店：库存量 > 平均库存量 + 安全库存的门店
    3. 确定调入门店：库存量 < 安全库存的门店
    4. 计算调拨数量：确保调出门店调出后仍有足够库存，调入门店调入后达到安全库存水平

    Args:
        product_id: 商品ID（可选），用于筛选特定商品的调拨方案
        user: 当前用户
        db: 数据库会话

    Returns:
        调拨方案列表
    """
    transfer_plans = InventoryService.get_transfer_plans(db, product_id, user)
    return TransferPlansResponse(transfer_plans=transfer_plans)


@inventory_router.put('/optimization/threshold/{product_id}', response_model=ThresholdUpdateResponse)
async def update_threshold(
        product_id: str,
        payload: ThresholdUpdateRequest,
        user: User = Depends(require_role('inventory_manager')),
        db: Session = Depends(get_db)
):
    """
    更新库存预警阈值接口

    单独设置商品的库存预警阈值（安全库存），用于库存优化和补货建议计算。

    Args:
        product_id: 商品ID
        payload: 预警阈值更新请求体
        user: 当前用户
        db: 数据库会话

    Returns:
        更新后的预警阈值信息
    """
    result = InventoryService.update_threshold(db, product_id, payload.warning_quantity, user)
    return ThresholdUpdateResponse(**result)

