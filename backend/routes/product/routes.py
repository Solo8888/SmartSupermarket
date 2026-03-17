
# 商品API路由
# 提供商品的增删改查接口

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import get_db, User
from core.permitions import require_role
from .schemas import ProductCreate, ProductResponse, ProductUpdate
from .service import ProductService
from fastapi_pagination import Page, Params

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


@product_router.get('/', response_model=Page[ProductResponse])
async def get_products(
        params: Params = Depends(),
        search: str = None,
        db: Session = Depends(get_db)
):
    """
    获取商品列表接口

    Args:
        params: 分页参数
        search: 搜索关键词（可选），支持搜索商品名称、品牌、条码
        db: 数据库会话

    Returns:
        商品列表（分页）
    """
    return ProductService.get_products(db, params, search)


@product_router.get('/all')
async def get_all_products(
        db: Session = Depends(get_db)
):
    """
    获取所有商品接口（不分页）

    Args:
        db: 数据库会话

    Returns:
        所有商品列表
    """
    return ProductService.get_all_products(db)


@product_router.get('/{product_id}', response_model=ProductResponse)
async def get_product(
        product_id: str,
        db: Session = Depends(get_db)
):
    """
    获取单个商品详情接口

    Args:
        product_id: 商品ID
        db: 数据库会话

    Returns:
        商品详情
    """
    product = ProductService.get_product(db, product_id)
    return ProductResponse(**product)


@product_router.put('/{product_id}', response_model=ProductResponse)
async def update_product(
        product_id: str,
        payload: ProductUpdate,
        user: User = Depends(require_role('inventory_manager')),
        db: Session = Depends(get_db)
):
    """
    更新商品接口

    Args:
        product_id: 商品ID
        payload: 更新商品请求体
        user: 当前用户
        db: 数据库会话

    Returns:
        更新成功的商品信息
    """
    product = ProductService.update_product(db, product_id, payload, user)
    return ProductResponse(**product)


@product_router.delete('/{product_id}', status_code=204)
async def delete_product(
        product_id: str,
        user: User = Depends(require_role('inventory_manager')),
        db: Session = Depends(get_db)
):
    """
    删除商品接口

    Args:
        product_id: 商品ID
        user: 当前用户
        db: 数据库会话
    """
    ProductService.delete_product(db, product_id, user)


@product_router.get('/category/{category_id}')
async def get_products_by_category(
        category_id: str,
        db: Session = Depends(get_db)
):
    """
    按分类获取商品接口

    Args:
        category_id: 分类ID
        db: 数据库会话

    Returns:
        该分类下的商品列表
    """
    return ProductService.get_products_by_category(db, category_id)

