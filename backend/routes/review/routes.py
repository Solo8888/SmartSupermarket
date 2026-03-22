# 评价API路由
# 提供评价的增删改查接口

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from models import get_db, User
from core.permitions import require_role
from .schemas import ReviewCreate, ReviewResponse
from .service import ReviewService
from fastapi_pagination import Page, Params
from typing import Optional

review_router = APIRouter(prefix='/reviews', tags=['reviews'])


@review_router.post('', response_model=ReviewResponse)
async def create_review(
        payload: ReviewCreate,
        user: User = Depends(require_role('customer')),
        db: Session = Depends(get_db)
):
    """
    创建评价接口

    Args:
        payload: 创建评价请求体
        user: 当前用户
        db: 数据库会话

    Returns:
        创建成功的评价信息
    """
    review = ReviewService.create_review(db, payload, user)
    return ReviewResponse(**review)


@review_router.get('/product/{product_id}', response_model=Page[ReviewResponse])
async def get_reviews_by_product(
        product_id: str,
        params: Params = Depends(),
        db: Session = Depends(get_db)
):
    """
    获取商品的评价列表接口（分页）

    Args:
        product_id: 商品ID
        params: 分页参数
        db: 数据库会话

    Returns:
        评价列表（分页）
    """
    result = ReviewService.get_reviews_by_product(db, product_id, params.page, params.size)
    return result


@review_router.get('/user', response_model=Page[ReviewResponse])
async def get_reviews_by_user(
        params: Params = Depends(),
        user: User = Depends(require_role('customer')),
        db: Session = Depends(get_db)
):
    """
    获取当前用户的评价列表接口（分页）

    Args:
        params: 分页参数
        user: 当前用户
        db: 数据库会话

    Returns:
        评价列表（分页）
    """
    result = ReviewService.get_reviews_by_user(db, user.id, params.page, params.size)
    return result


@review_router.post('/auto')
async def auto_review(
        db: Session = Depends(get_db)
):
    """
    自动评价接口：7天未评价的已收货订单默认好评

    Args:
        db: 数据库会话

    Returns:
        操作结果
    """
    ReviewService.auto_review(db)
    return {"message": "自动评价完成"}
