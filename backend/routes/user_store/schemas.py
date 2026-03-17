# 门店分配数据模型
# 定义门店分配相关的请求和响应数据模型

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StoreAllocationCreate(BaseModel):
    """创建门店分配请求"""
    user_id: str = Field(..., description="用户ID")
    store_id: str = Field(..., description="门店ID")


class StoreAllocationResponse(BaseModel):
    """门店分配响应"""
    id: str
    user_id: str
    store_id: str
    created_at: datetime

    class Config:
        from_attributes = True


class UserStoreListResponse(BaseModel):
    """用户门店列表响应"""
    id: str
    store_id: str
    store_name: str
    created_at: datetime


class StoreUserListResponse(BaseModel):
    """门店用户列表响应"""
    id: str
    user_id: str
    username: str
    role: str
    created_at: datetime
