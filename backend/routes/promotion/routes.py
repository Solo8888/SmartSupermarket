# 促销活动API路由
# 提供促销活动的增删改查接口

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import get_db, User
from core.permitions import require_role
from .schemas import PromotionCreate, PromotionResponse, PromotionUpdate
from .service import PromotionService
from fastapi_pagination import Page, Params

promotion_router = APIRouter(prefix='/promotions', tags=['promotions'])


@promotion_router.post('/', response_model=PromotionResponse)
async def create_promotion(
        payload: PromotionCreate,
        user: User = Depends(require_role('inventory_manager')),
        db: Session = Depends(get_db)
):
    """
    创建促销活动接口

    Args:
        payload: 创建促销活动请求体
        user: 当前用户
        db: 数据库会话

    Returns:
        创建成功的促销活动信息
    """
    promotion = PromotionService.create_promotion(db, payload, user)
    return PromotionResponse(**promotion)


@promotion_router.get('/', response_model=Page[PromotionResponse])
async def get_promotions(
        params: Params = Depends(),
        db: Session = Depends(get_db)
):
    """
    获取促销活动列表接口（分页）

    Args:
        params: 分页参数
        db: 数据库会话

    Returns:
        促销活动列表（分页）
    """
    return PromotionService.get_promotions(db, params)


@promotion_router.get('/{promotion_id}', response_model=PromotionResponse)
async def get_promotion(
        promotion_id: str,
        db: Session = Depends(get_db)
):
    """
    获取单个促销活动详情接口

    Args:
        promotion_id: 促销活动ID
        db: 数据库会话

    Returns:
        促销活动详情
    """
    promotion = PromotionService.get_promotion(db, promotion_id)
    return PromotionResponse(**promotion)


@promotion_router.put('/{promotion_id}', response_model=PromotionResponse)
async def update_promotion(
        promotion_id: str,
        payload: PromotionUpdate,
        user: User = Depends(require_role('inventory_manager')),
        db: Session = Depends(get_db)
):
    """
    更新促销活动接口

    Args:
        promotion_id: 促销活动ID
        payload: 更新促销活动请求体
        user: 当前用户
        db: 数据库会话

    Returns:
        更新成功的促销活动信息
    """
    promotion = PromotionService.update_promotion(db, promotion_id, payload, user)
    return PromotionResponse(**promotion)


@promotion_router.delete('/{promotion_id}', status_code=204)
async def delete_promotion(
        promotion_id: str,
        user: User = Depends(require_role('inventory_manager')),
        db: Session = Depends(get_db)
):
    """
    删除促销活动接口

    Args:
        promotion_id: 促销活动ID
        user: 当前用户
        db: 数据库会话
    """
    PromotionService.delete_promotion(db, promotion_id, user)
