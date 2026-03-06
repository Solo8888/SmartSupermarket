
# 商品数据模型
# 定义商品相关的请求和响应数据模型

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class ProductCreate(BaseModel):
    """创建商品请求"""
    name: str = Field(..., description="商品名称", max_length=100)
    category_id: int = Field(..., description="分类ID")
    price: Decimal = Field(..., description="商品价格", ge=0)
    original_price: Optional[Decimal] = Field(None, description="原价", ge=0)
    description: Optional[str] = Field(None, description="商品描述")
    image_url: Optional[str] = Field(None, description="商品图片URL", max_length=255)
    barcode: Optional[str] = Field(None, description="商品条码", max_length=50)
    brand: Optional[str] = Field(None, description="品牌", max_length=50)
    unit: str = Field("个", description="单位", max_length=20)
    status: str = Field("active", description="状态", pattern="^(active|inactive|out_of_stock)$")


class ProductUpdate(BaseModel):
    """更新商品请求"""
    name: Optional[str] = Field(None, description="商品名称", max_length=100)
    category_id: Optional[int] = Field(None, description="分类ID")
    price: Optional[Decimal] = Field(None, description="商品价格", ge=0)
    original_price: Optional[Decimal] = Field(None, description="原价", ge=0)
    description: Optional[str] = Field(None, description="商品描述")
    image_url: Optional[str] = Field(None, description="商品图片URL", max_length=255)
    barcode: Optional[str] = Field(None, description="商品条码", max_length=50)
    brand: Optional[str] = Field(None, description="品牌", max_length=50)
    unit: Optional[str] = Field(None, description="单位", max_length=20)
    status: Optional[str] = Field(None, description="状态", pattern="^(active|inactive|out_of_stock)$")


class ProductResponse(BaseModel):
    """商品响应"""
    id: int
    name: str
    category_id: int
    price: Decimal
    original_price: Optional[Decimal] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    barcode: Optional[str] = None
    brand: Optional[str] = None
    unit: str
    status: str
    sales_count: int
    view_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

