# 商品类别API路由
# 提供商品类别的增删改查接口

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import get_db, User
from core.permitions import require_role
from .schemas import CategoryCreate, CategoryResponse, CategoryUpdate
from .service import CategoryService
from fastapi_pagination import Page, Params
from typing import List

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


@category_router.get('/', response_model=Page[CategoryResponse])
async def get_categories(
        params: Params = Depends(),
        db: Session = Depends(get_db)
):
    """
    获取商品类别列表接口（分页）

    Args:
        params: 分页参数
        db: 数据库会话

    Returns:
        商品类别列表（分页）
    """
    return CategoryService.get_categories(db, params)


@category_router.get('/all', response_model=List[CategoryResponse])
async def get_all_categories(
        db: Session = Depends(get_db)
):
    """
    获取所有商品类别接口（不分页）

    Args:
        db: 数据库会话

    Returns:
        所有商品类别列表
    """
    categories = CategoryService.get_all_categories(db)
    return [CategoryResponse(**cat) for cat in categories]


@category_router.get('/{category_id}', response_model=CategoryResponse)
async def get_category(
        category_id: int,
        db: Session = Depends(get_db)
):
    """
    获取单个商品类别详情接口

    Args:
        category_id: 商品类别ID
        db: 数据库会话

    Returns:
        商品类别详情
    """
    category = CategoryService.get_category(db, category_id)
    return CategoryResponse(**category)


@category_router.put('/{category_id}', response_model=CategoryResponse)
async def update_category(
        category_id: int,
        payload: CategoryUpdate,
        user: User = Depends(require_role('inventory_manager')),
        db: Session = Depends(get_db)
):
    """
    更新商品类别接口

    Args:
        category_id: 商品类别ID
        payload: 更新商品类别请求体
        user: 当前用户
        db: 数据库会话

    Returns:
        更新成功的商品类别信息
    """
    category = CategoryService.update_category(db, category_id, payload, user)
    return CategoryResponse(**category)


@category_router.delete('/{category_id}', status_code=204)
async def delete_category(
        category_id: int,
        user: User = Depends(require_role('inventory_manager')),
        db: Session = Depends(get_db)
):
    """
    删除商品类别接口

    Args:
        category_id: 商品类别ID
        user: 当前用户
        db: 数据库会话
    """
    CategoryService.delete_category(db, category_id, user)
