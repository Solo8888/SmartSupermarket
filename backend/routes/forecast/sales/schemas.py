from pydantic import BaseModel
from datetime import date
from typing import List, Optional


class ForecastBase(BaseModel):
    """
    预测基础模型
    """
    product_id: str
    forecast_date: date
    predicted_sales: float
    confidence: float


class ForecastCreate(ForecastBase):
    """
    创建预测模型
    """
    pass


class ForecastResponse(ForecastBase):
    """
    预测响应模型
    """
    id: int
    adjusted_value: Optional[float] = None

    class Config:
        from_attributes = True


class ForecastListResponse(BaseModel):
    """
    预测列表响应模型
    """
    product_id: str
    forecast: List[ForecastResponse]


class ForecastAdjustmentBase(BaseModel):
    """
    预测调整基础模型
    """
    adjusted_value: float
    reason: str


class ForecastAdjustmentCreate(ForecastAdjustmentBase):
    """
    创建预测调整模型
    """
    pass


class ForecastAdjustmentResponse(ForecastAdjustmentBase):
    """
    预测调整响应模型
    """
    id: int
    forecast_id: int

    class Config:
        from_attributes = True


class ExportRequest(BaseModel):
    """
    导出请求模型
    """
    format: str = "excel"
    product_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None