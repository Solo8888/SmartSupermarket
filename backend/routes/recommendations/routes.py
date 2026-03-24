# 推荐系统API路由
# 提供个性化商品推荐接口

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from models import get_db, User
from core.permitions import require_role
from .schemas import RecommendationRequest, RecommendationResponse
from .service import RecommendationService

recommendation_router = APIRouter(prefix='/recommendations', tags=['recommendations'])


@recommendation_router.post('/personalized', response_model=RecommendationResponse)
async def get_personalized_recommendations(
        request: RecommendationRequest,
        user: User = Depends(require_role(['customer', 'system_admin'], mode='in')),
        db: Session = Depends(get_db)
):
    """
    获取个性化商品推荐接口

    Args:
        request: 推荐请求参数
        user: 当前用户
        db: 数据库会话

    Returns:
        个性化推荐结果
    """
    result = RecommendationService.get_personalized_recommendations(db, user, request)
    return RecommendationResponse(**result)


@recommendation_router.get('/new-user', response_model=RecommendationResponse)
async def get_new_user_recommendations(
        store_id: str = Query(None, description="门店ID，可选"),
        limit: int = Query(20, ge=1, le=100, description="推荐商品数量限制"),
        db: Session = Depends(get_db)
):
    """
    获取新用户推荐接口（无需登录）

    Args:
        store_id: 门店ID（可选）
        limit: 推荐商品数量限制
        db: 数据库会话

    Returns:
        新用户推荐结果
    """
    request = RecommendationRequest(store_id=store_id, limit=limit)
    result = RecommendationService.get_new_user_recommendations(db, request)
    return RecommendationResponse(**result)