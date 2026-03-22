# 评价数据模型
# 定义评价相关的请求和响应数据模型

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    """创建评价请求"""
    order_item_id: str = Field(..., description="订单项ID")
    rating: int = Field(..., description="评分（1-5星）", ge=1, le=5)
    content: Optional[str] = Field(None, description="评价内容")


class ReviewResponse(BaseModel):
    """评价响应"""
    id: str
    order_id: str
    order_item_id: str
    user_id: Optional[str] = None
    product_id: Optional[str] = None
    rating: int
    content: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True
