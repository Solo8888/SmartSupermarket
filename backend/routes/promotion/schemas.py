# 促销活动数据模型
# 定义促销活动相关的请求和响应数据模型

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal


class PromotionCreate(BaseModel):
    """创建促销活动请求"""
    name: str = Field(..., description="促销活动名称", max_length=100)
    description: Optional[str] = Field(None, description="促销活动描述")
    type: str = Field(..., description="促销类型", pattern="^(discount|special_price|buy_x_get_y|bundle)$")
    value: Decimal = Field(..., description="促销值（折扣率或减价金额）", gt=0)
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    status: str = Field("draft", description="状态", pattern="^(draft|active|paused|ended)$")


class PromotionUpdate(BaseModel):
    """更新促销活动请求"""
    name: Optional[str] = Field(None, description="促销活动名称", max_length=100)
    description: Optional[str] = Field(None, description="促销活动描述")
    type: Optional[str] = Field(None, description="促销类型", pattern="^(discount|special_price|buy_x_get_y|bundle)$")
    value: Optional[Decimal] = Field(None, description="促销值（折扣率或减价金额）", gt=0)
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    status: Optional[str] = Field(None, description="状态", pattern="^(draft|active|paused|ended)$")


class PromotionResponse(BaseModel):
    """促销活动响应"""
    id: str
    name: str
    description: Optional[str] = None
    type: str
    value: Decimal
    start_time: datetime
    end_time: datetime
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
