# 促销活动API路由
# 提供促销活动的增删改查接口

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import get_db, User
from core.permitions import require_role
from .schemas import PromotionCreate, PromotionResponse
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
