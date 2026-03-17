# 商品类别数据模型
# 定义商品类别相关的请求和响应数据模型

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CategoryCreate(BaseModel):
    """创建商品类别请求"""
    name: str = Field(..., description="分类名称", max_length=50)
    parent_id: Optional[str] = Field(None, description="父分类ID")
    description: Optional[str] = Field(None, description="分类描述")
    sort_order: int = Field(0, description="排序顺序", ge=0)


class CategoryUpdate(BaseModel):
    """更新商品类别请求"""
    name: Optional[str] = Field(None, description="分类名称", max_length=50)
    parent_id: Optional[str] = Field(None, description="父分类ID")
    store_id: Optional[str] = Field(None, description="门店ID")
    description: Optional[str] = Field(None, description="分类描述")
    sort_order: Optional[int] = Field(None, description="排序顺序", ge=0)


class CategoryResponse(BaseModel):
    """商品类别响应"""
    id: str
    name: str
    parent_id: Optional[str] = None
    store_id: str
    description: Optional[str] = None
    sort_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
