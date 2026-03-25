from pydantic import BaseModel
from datetime import date, time
from typing import List, Optional


class CustomerFlowBase(BaseModel):
    """客流基础模型"""
    store_id: str
    flow_date: date
    hour: int
    flow_count: int


class CustomerFlowCreate(CustomerFlowBase):
    """创建客流记录模型"""
    pass


class CustomerFlowResponse(CustomerFlowBase):
    """客流响应模型"""
    id: int

    class Config:
        from_attributes = True


class CustomerFlowHourlyRequest(BaseModel):
    """获取各时段客流分布请求模型"""
    store_id: str
    start_date: date
    end_date: date


class CustomerFlowHourlyItem(BaseModel):
    """各时段客流分布项"""
    hour: int
    flow_count: int


class CustomerFlowHourlyResponse(BaseModel):
    """各时段客流分布响应模型"""
    store_id: str
    start_date: date
    end_date: date
    data: List[CustomerFlowHourlyItem]
