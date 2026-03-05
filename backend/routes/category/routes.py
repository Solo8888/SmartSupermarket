# 商品类别API路由
# 提供商品类别的增删改查接口

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import get_db, User
from core.permitions import require_role
from .schemas import CategoryCreate, CategoryResponse
from .service import CategoryService

category_router = APIRouter(prefix='/categories', tags=['categories'])


@category_router.post('/', response_model=CategoryResponse)
async def create_category(
        payload: CategoryCreate,
        user: User = Depends(require_role('inventory_manager')),
        db: Session = Depends(get_db)
):
    """
    创建商品类别接口

    Args:
        payload: 创建商品类别请求体
        user: 当前用户
        db: 数据库会话

    Returns:
        创建成功的商品类别信息
    """
    category = CategoryService.create_category(db, payload, user)
    return CategoryResponse(**category)
    
