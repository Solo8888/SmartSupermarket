from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import date, datetime
from typing import Optional
import pandas as pd
from io import BytesIO

from models import get_db
from core.permitions import require_role
from .schemas import (
    ForecastResponse, 
    ForecastListResponse, 
    ForecastAdjustmentCreate, 
    ExportRequest
)
from .service import get_forecasts, adjust_forecast, get_forecasts_for_export

router = APIRouter(prefix="/forecast", tags=["forecast"])


@router.get("/sales", response_model=ForecastListResponse)
async def get_sales_forecast(
    product_id: str = Query(..., description="商品ID"),
    forecast_period: str = Query("short", description="预测周期 (short/medium/long)"),
    start_date: date = Query(..., description="开始日期"),
    db: Session = Depends(get_db),
    user = Depends(require_role("inventory_manager"))
):
    """
    获取销量预测
    
    - **product_id**: 商品ID
    - **forecast_period**: 预测周期 (short/medium/long)
    - **start_date**: 开始日期
    """
    forecasts = get_forecasts(db, product_id, forecast_period, start_date)
    if not forecasts:
        raise HTTPException(status_code=404, detail="商品不存在或无法生成预测")
    
    forecast_responses = [
        ForecastResponse(
            id=forecast.id,
            product_id=forecast.product_id,
            forecast_date=forecast.forecast_date,
            predicted_sales=forecast.predicted_sales,
            confidence=forecast.confidence,
            adjusted_value=forecast.adjusted_value
        )
        for forecast in forecasts
    ]
    
    return ForecastListResponse(
        product_id=product_id,
        forecast=forecast_responses
    )


@router.put("/sales/{forecast_id}/adjust")
async def adjust_sales_forecast(
    forecast_id: int,
    adjustment: ForecastAdjustmentCreate,
    db: Session = Depends(get_db),
    user = Depends(require_role("inventory_manager"))
):
    """
    调整预测结果
    
    - **forecast_id**: 预测ID
    - **adjusted_value**: 调整后的值
    - **reason**: 调整原因
    """
    forecast = adjust_forecast(
        db, 
        forecast_id, 
        adjustment.adjusted_value, 
        adjustment.reason
    )
    
    if not forecast:
        raise HTTPException(status_code=404, detail="预测不存在")
    
    return ForecastResponse(
        id=forecast.id,
        product_id=forecast.product_id,
        forecast_date=forecast.forecast_date,
        predicted_sales=forecast.predicted_sales,
        confidence=forecast.confidence,
        adjusted_value=forecast.adjusted_value
    )

@router.post("/sales/export")
async def export_sales_forecast(
    export_request: ExportRequest,
    db: Session = Depends(get_db),
    user = Depends(require_role("inventory_manager"))
):
    """
    导出预测结果
    
    - **format**: 导出格式 (excel)
    - **product_id**: 商品ID（可选）
    - **start_date**: 开始日期（可选）
    - **end_date**: 结束日期（可选）
    """
    # 获取预测数据
    forecasts = get_forecasts_for_export(
        db,
        export_request.product_id,
        export_request.start_date,
        export_request.end_date
    )
    
    if not forecasts:
        raise HTTPException(status_code=404, detail="没有找到预测数据")
    
    # 准备数据
    data = []
    for forecast in forecasts:
        data.append({
            "预测ID": forecast.id,
            "商品ID": forecast.product_id,
            "预测日期": forecast.forecast_date,
            "预测销量": forecast.predicted_sales,
            "置信度": forecast.confidence,
            "调整后销量": forecast.adjusted_value or "-"
        })
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    
    # 生成Excel文件
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='销量预测')
    
    output.seek(0)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"sales_forecast_{timestamp}.xlsx"
    
    # 返回文件
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )