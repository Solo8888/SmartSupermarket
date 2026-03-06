
# 商品API路由
# 提供商品的增删改查接口

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import get_db, User
from core.permitions import require_role
from .schemas import ProductCreate, ProductResponse
from .service import ProductService

product_router = APIRouter(prefix='/products', tags=['products'])


@product_router.post('/', response_model=ProductResponse)
async def create_product(
        payload: ProductCreate,
        user: User = Depends(require_role('inventory_manager')),
        db: Session = Depends(get_db)
):
    """
    创建商品接口

    Args:
        payload: 创建商品请求体
        user: 当前用户
        db: 数据库会话

    Returns:
        创建成功的商品信息
    """
    product = ProductService.create_product(db, payload, user)
    return ProductResponse(**product)

