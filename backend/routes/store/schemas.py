# 门店数据模型
# 定义门店相关的请求和响应数据模型

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StoreCreate(BaseModel):
    """创建门店请求"""
    name: str = Field(..., description="门店名称", max_length=100)
    address: str = Field(..., description="门店地址")
    phone: str = Field(..., description="联系电话", max_length=20)
    opening_hours: str = Field(..., description="营业时间", max_length=100)
    status: str = Field('active', description="门店状态")


class StoreUpdate(BaseModel):
    """更新门店请求"""
    name: Optional[str] = Field(None, description="门店名称", max_length=100)
    address: Optional[str] = Field(None, description="门店地址")
    phone: Optional[str] = Field(None, description="联系电话", max_length=20)
    opening_hours: Optional[str] = Field(None, description="营业时间", max_length=100)
    status: Optional[str] = Field(None, description="门店状态")


class StoreResponse(BaseModel):
    """门店响应"""
    id: str
    name: str
    address: str
    phone: str
    opening_hours: str
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
