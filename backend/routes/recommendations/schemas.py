# 推荐系统数据模型
# 定义推荐相关的请求和响应数据模型

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class RecommendationRequest(BaseModel):
    """推荐请求"""
    store_id: Optional[str] = Field(None, description="门店ID，可选")
    limit: int = Field(20, description="推荐商品数量限制", ge=1, le=100)


class RecommendedProduct(BaseModel):
    """推荐商品"""
    id: str
    name: str
    category_id: str
    store_id: str
    price: Decimal
    original_price: Optional[Decimal] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    stock: int
    sales_count: int
    view_count: int
    score: float = Field(..., description="推荐分数")
    reason: str = Field(..., description="推荐理由")


class RecommendationResponse(BaseModel):
    """推荐响应"""
    products: List[RecommendedProduct]
    total: int
    algorithm: str = Field(..., description="使用的推荐算法")
    explanation: str = Field(..., description="算法说明")