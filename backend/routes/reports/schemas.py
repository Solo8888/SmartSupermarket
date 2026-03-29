# Reports data models
# Define request and response models for reports

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from decimal import Decimal


class RecommendationConversionRequest(BaseModel):
    """推荐转化率分析请求"""
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    store_id: Optional[str] = Field(None, description="门店ID")
    category_id: Optional[str] = Field(None, description="商品分类ID")
    time_granularity: Optional[str] = Field("day", description="时间粒度: day, week, month")
    include_details: Optional[bool] = Field(False, description="是否包含详细数据")


class RecommendationConversionMetrics(BaseModel):
    """推荐转化指标"""
    impressions: int = Field(..., description="推荐展示次数")
    clicks: int = Field(..., description="点击次数")
    add_to_carts: int = Field(..., description="加购次数")
    purchases: int = Field(..., description="购买次数")
    click_rate: float = Field(..., description="点击率")
    cart_rate: float = Field(..., description="加购率")
    purchase_rate: float = Field(..., description="购买率")
    conversion_rate: float = Field(..., description="整体转化率")


class RecommendationConversionTrend(BaseModel):
    """推荐转化趋势"""
    date: str = Field(..., description="日期")
    metrics: RecommendationConversionMetrics = Field(..., description="转化指标")


class RecommendationConversionDetail(BaseModel):
    """推荐转化详细数据"""
    recommendation_id: str = Field(..., description="推荐记录ID")
    user_id: Optional[str] = Field(None, description="用户ID")
    product_id: str = Field(..., description="商品ID")
    product_name: str = Field(..., description="商品名称")
    store_id: str = Field(..., description="门店ID")
    category_id: str = Field(..., description="分类ID")
    recommended_at: datetime = Field(..., description="推荐时间")
    clicked_at: Optional[datetime] = Field(None, description="点击时间")
    added_to_cart_at: Optional[datetime] = Field(None, description="加购时间")
    purchased_at: Optional[datetime] = Field(None, description="购买时间")
    status: str = Field(..., description="转化状态: impression, click, add_to_cart, purchase")


class RecommendationConversionResponse(BaseModel):
    """推荐转化率分析响应"""
    summary: RecommendationConversionMetrics = Field(..., description="汇总指标")
    trends: List[RecommendationConversionTrend] = Field(default_factory=list, description="趋势数据")
    details: List[RecommendationConversionDetail] = Field(default_factory=list, description="详细数据")
    filters: Dict[str, Any] = Field(default_factory=dict, description="应用的过滤器")
    generated_at: datetime = Field(default_factory=datetime.now, description="生成时间")


class ExportRequest(BaseModel):
    """导出请求"""
    report_type: str = Field(..., description="报表类型: recommendation_conversion")
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    store_id: Optional[str] = Field(None, description="门店ID")
    category_id: Optional[str] = Field(None, description="商品分类ID")
    format: str = Field("csv", description="导出格式: csv, excel, json")


class ExportResponse(BaseModel):
    """导出响应"""
    file_url: str = Field(..., description="导出文件的URL")
    file_name: str = Field(..., description="导出文件的名称")
    format: str = Field(..., description="导出格式")
    size: int = Field(..., description="文件大小(字节)")
    generated_at: datetime = Field(default_factory=datetime.now, description="生成时间")