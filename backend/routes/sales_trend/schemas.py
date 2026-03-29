# Data models for sales trend analysis
from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal


class SalesTrendData(BaseModel):
    """销售趋势数据"""
    period: str  # 时间周期标识 (如: "2024-01-01" 或 "2024-W01" 或 "2024-01")
    total_sales: Decimal  # 总销售额
    order_count: int  # 订单数量
    average_order_value: Decimal  # 平均订单价值


class SalesTrendResponse(BaseModel):
    """销售趋势响应"""
    data: List[SalesTrendData]


class SalesTrendQuery(BaseModel):
    """销售趋势查询参数"""
    start_date: Optional[str] = None  # 格式: YYYY-MM-DD
    end_date: Optional[str] = None  # 格式: YYYY-MM-DD
    store_id: Optional[str] = None  # 门店ID（可选）
    category_id: Optional[str] = None  # 商品分类ID（可选）
    period: str = "daily"  # 时间周期 (daily/weekly/monthly)
