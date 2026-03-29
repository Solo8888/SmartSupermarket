# Sales Trend API routes
# Provides API endpoints for sales trend analysis

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from .schemas import SalesTrendResponse, SalesTrendQuery
from .service import SalesTrendService
from core.permitions import require_role

sales_trend_router = APIRouter(
    prefix="",
    tags=["sales-trend"],
    responses={404: {"description": "Not found"}},
)

sales_trend_service = SalesTrendService()


@sales_trend_router.get("/sales-trend", response_model=SalesTrendResponse)
async def get_sales_trend(
    start_date: Optional[str] = Query(None, description="开始日期 (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="结束日期 (YYYY-MM-DD)"),
    store_id: Optional[str] = Query(None, description="门店ID（可选）"),
    category_id: Optional[str] = Query(None, description="商品分类ID（可选）"),
    period: Optional[str] = Query("daily", description="时间周期 (daily/weekly/monthly)"),
    current_user = Depends(require_role(["operations_manager", "store_manager"], mode="in"))
):
    """获取销售趋势数据
    
    - **start_date**: 开始日期 (YYYY-MM-DD)，默认最近30天
    - **end_date**: 结束日期 (YYYY-MM-DD)，默认今天
    - **store_id**: 门店ID（可选）
    - **category_id**: 商品分类ID（可选）
    - **period**: 时间周期 (daily/weekly/monthly)，默认daily
    """
    try:
        if period not in ["daily", "weekly", "monthly"]:
            raise HTTPException(status_code=400, detail="不支持的时间周期，支持的周期：daily, weekly, monthly")
        
        data = sales_trend_service.get_sales_trend(
            start_date=start_date,
            end_date=end_date,
            store_id=store_id,
            category_id=category_id,
            period=period
        )
        
        return SalesTrendResponse(data=data)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取销售趋势数据失败: {str(e)}")
