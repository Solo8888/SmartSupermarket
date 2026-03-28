# Data models for footfall analytics
from pydantic import BaseModel, Field
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


class ExportRequest(BaseModel):
    """导出请求参数"""
    start_date: str = Field(..., description="开始日期 (YYYY-MM-DD)")
    end_date: str = Field(..., description="结束日期 (YYYY-MM-DD)")
    store_id: Optional[str] = Field(None, description="门店ID（可选）")
    format: str = Field(..., description="导出格式 (pdf/excel)")


class WeekComparisonData(BaseModel):
    """周对比数据"""
    hour: str  # 格式: "HH:00"
    this_week: int  # 本周客流
    last_week: int  # 上周客流


class WeekComparisonResponse(BaseModel):
    """周对比响应"""
    data: List[WeekComparisonData]


class WeekendWeekdayData(BaseModel):
    """周末工作日对比数据"""
    hour: str  # 格式: "HH:00"
    this_week_weekday: float  # 本周工作日平均客流
    this_week_weekend: float  # 本周周末平均客流
    last_week_weekday: float  # 上周工作日平均客流
    last_week_weekend: float  # 上周周末平均客流


class WeekendWeekdayResponse(BaseModel):
    """周末工作日对比响应"""
    data: List[WeekendWeekdayData]


class ForecastData(BaseModel):
    """预测客流数据"""
    hour: int  # 小时 (0-23)
    forecast_count: int  # 预测客流量


class ForecastResponse(BaseModel):
    """预测响应"""
    data: List[ForecastData]