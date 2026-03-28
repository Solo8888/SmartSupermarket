# 客流数据模式定义
# 定义客流数据的请求和响应模型

from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class CustomerFlowBase(BaseModel):
    """客流数据基础模型"""
    store_id: str
    timestamp: datetime
    customer_count: int
    hour: int
    weekday: int


class CustomerFlowResponse(CustomerFlowBase):
    """客流数据响应模型"""
    class Config:
        from_attributes = True


class CustomerFlowQuery(BaseModel):
    """客流数据查询模型"""
    start_time: datetime
    end_time: datetime
    store_id: Optional[str] = None


class CustomerFlowListResponse(BaseModel):
    """客流数据列表响应模型"""
    data: List[CustomerFlowResponse]
    total: int