# 地址簿相关的数据模型
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AddressBase(BaseModel):
    """地址基础模型"""
    name: str = Field(..., description="收件人姓名")
    phone: str = Field(..., description="联系电话")
    province: str = Field(..., description="省份")
    city: str = Field(..., description="城市")
    district: str = Field(..., description="区县")
    address: str = Field(..., description="详细地址")
    is_default: bool = Field(False, description="是否默认地址")


class AddressCreate(AddressBase):
    """创建地址请求模型"""
    pass


class AddressUpdate(AddressBase):
    """更新地址请求模型"""
    pass


class AddressResponse(AddressBase):
    """地址响应模型"""
    id: str
    user_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
