
# 商品数据模型
# 定义商品相关的请求和响应数据模型

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProductCreate(BaseModel):
    """创建商品请求"""
    name: str = Field(..., description="商品名称", max_length=200)
    category_id: Optional[int] = Field(None, description="分类ID")
    barcode: Optional[str] = Field(None, description="商品条码", max_length=50)
    description: Optional[str] = Field(None, description="商品描述")
    price: Decimal = Field(..., description="商品价格", ge=0)
    cost_price: Optional[Decimal] = Field(None, description="成本价格", ge=0)
    image_url: Optional[str] = Field(None, description="商品图片URL", max_length=500)
    status: str = Field("active", description="状态", pattern="^(active|inactive|out_of_stock)$")
    sort_order: int = Field(0, description="排序顺序", ge=0)


class ProductUpdate(BaseModel):
    """更新商品请求"""
    name: Optional[str] = Field(None, description="商品名称", max_length=200)
    category_id: Optional[int] = Field(None, description="分类ID")
    barcode: Optional[str] = Field(None, description="商品条码", max_length=50)
    description: Optional[str] = Field(None, description="商品描述")
    price: Optional[Decimal] = Field(None, description="商品价格", ge=0)
    cost_price: Optional[Decimal] = Field(None, description="成本价格", ge=0)
    image_url: Optional[str] = Field(None, description="商品图片URL", max_length=500)
    status: Optional[str] = Field(None, description="状态", pattern="^(active|inactive|out_of_stock)$")
    sort_order: Optional[int] = Field(None, description="排序顺序", ge=0)


class ProductResponse(BaseModel):
    """商品响应"""
    id: int
    name: str
    category_id: Optional[int] = None
    barcode: Optional[str] = None
    description: Optional[str] = None
    price: Decimal
    cost_price: Optional[Decimal] = None
    image_url: Optional[str] = None
    status: str
    sort_order: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

