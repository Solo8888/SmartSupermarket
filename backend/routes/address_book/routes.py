# 地址簿API路由
# 提供地址簿的增删改查接口

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models import get_db
from core.auth import get_current_user_id
from typing import List
from .schemas import AddressCreate, AddressResponse
from .service import AddressService

address_router = APIRouter(prefix='/addresses', tags=['addresses'])


@address_router.post('', response_model=AddressResponse)
async def create_address(
        payload: AddressCreate,
        db: Session = Depends(get_db),
        current_user_id: str = Depends(get_current_user_id)
):
    """
    添加地址到地址簿接口

    Args:
        payload: 创建地址请求体
        db: 数据库会话
        current_user_id: 当前用户ID

    Returns:
        创建成功的地址信息
    """
    address = AddressService.create_address(db, payload, current_user_id)
    return AddressResponse(**address)


@address_router.get('', response_model=List[AddressResponse])
async def get_addresses(
        db: Session = Depends(get_db),
        current_user_id: str = Depends(get_current_user_id)
):
    """
    获取用户地址列表接口

    Args:
        db: 数据库会话
        current_user_id: 当前用户ID

    Returns:
        用户的地址列表
    """
    addresses = AddressService.get_addresses(db, current_user_id)
    return [AddressResponse(**address) for address in addresses]
