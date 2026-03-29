# Reports routes
# Provides API endpoints for reports

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from core.permitions import require_role
from models import get_db
from .schemas import RecommendationConversionRequest, RecommendationConversionResponse, ExportRequest, ExportResponse
from .service import ReportsService

reports_router = APIRouter(prefix='/reports', tags=['reports'])


@reports_router.get('/recommendation-conversion', response_model=RecommendationConversionResponse)
async def get_recommendation_conversion(
    start_date: str = None,
    end_date: str = None,
    store_id: str = None,
    category_id: str = None,
    time_granularity: str = 'day',
    include_details: bool = False,
    current_user = Depends(require_role(['system_admin', 'operations_manager'], mode='in')),
    db: Session = Depends(get_db)
):
    """
    获取推荐转化率分析

    分析推荐系统的转化效果，包括推荐点击率、加购率、购买率等关键指标。
    支持按时间范围、门店、商品分类等维度分析。

    Args:
        start_date: 开始日期 (YYYY-MM-DD)
        end_date: 结束日期 (YYYY-MM-DD)
        store_id: 门店ID
        category_id: 商品分类ID
        time_granularity: 时间粒度 (day, week, month)
        include_details: 是否包含详细数据
        current_user: 当前用户
        db: 数据库会话

    Returns:
        推荐转化率分析结果
    """
    try:
        # 构建请求参数
        request = RecommendationConversionRequest(
            start_date=start_date,
            end_date=end_date,
            store_id=store_id,
            category_id=category_id,
            time_granularity=time_granularity,
            include_details=include_details
        )

        # 调用服务获取分析结果
        result = ReportsService.get_recommendation_conversion(db, request)

        # 构建响应
        response = RecommendationConversionResponse(
            summary=result['summary'],
            trends=result['trends'],
            details=result['details'],
            filters=result['filters']
        )

        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取推荐转化率分析失败: {str(e)}")


@reports_router.post('/export', response_model=ExportResponse)
async def export_report(
    request: ExportRequest,
    current_user = Depends(require_role(['system_admin', 'operations_manager'], mode='in')),
    db: Session = Depends(get_db)
):
    """
    导出报表

    导出各种报表数据，支持 JSON、CSV 和 Excel 格式。

    Args:
        request: 导出请求参数
        current_user: 当前用户
        db: 数据库会话

    Returns:
        导出结果，包含文件 URL 和相关信息
    """
    try:
        # 调用服务导出报表
        result = ReportsService.export_report(db, request)

        # 构建响应
        response = ExportResponse(
            file_url=result['file_url'],
            file_name=result['file_name'],
            format=result['format'],
            size=result['size']
        )

        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"导出报表失败: {str(e)}")