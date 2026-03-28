# Data models for footfall analytics
from pydantic import BaseModel
from typing import List, Optional


class HourlyFootfall(BaseModel):
    """小时客流分布数据"""
    hour: str  # 格式: "HH:00"
    count: int  # 客流量


class TimeDistributionResponse(BaseModel):
    """时间分布响应"""
    data: List[HourlyFootfall]


class TimeDistributionQuery(BaseModel):
    """时间分布查询参数"""
    start_date: str  # 格式: YYYY-MM-DD
    end_date: str  # 格式: YYYY-MM-DD
    store_id: Optional[str] = None  # 门店ID（可选）