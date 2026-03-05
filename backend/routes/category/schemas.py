# 商品类别数据模型
# 定义商品类别相关的请求和响应数据模型

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CategoryBase(BaseModel):
    """商品类别基础模型"""
    name: str = Field(..., description="分类名称", max_length=50)
    parent_id: Optional[int] = Field(None, description="父分类ID")
    description: Optional[str] = Field(None, description="分类描述")
    level: int = Field(1, description="分类级别", ge=1)
    sort_order: int = Field(0, description="排序顺序", ge=0)
    status: str = Field("active", description="状态", pattern="^(active|inactive)$")


class CategoryCreate(CategoryBase):
    """创建商品类别请求模型"""
    pass


class CategoryUpdate(BaseModel):
    """更新商品类别请求模型"""
    name: Optional[str] = Field(None, description="分类名称", max_length=50)
    parent_id: Optional[int] = Field(None, description="父分类ID")
    description: Optional[str] = Field(None, description="分类描述")
    level: Optional[int] = Field(None, description="分类级别", ge=1)
    sort_order: Optional[int] = Field(None, description="排序顺序", ge=0)
    status: Optional[str] = Field(None, description="状态", pattern="^(active|inactive)$")


class CategoryResponse(CategoryBase):
    """商品类别响应模型"""
    id: int = Field(..., description="分类ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True