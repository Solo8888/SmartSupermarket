# Footfall analytics routes
# Provides API endpoints for footfall analysis

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from .schemas import TimeDistributionResponse, TimeDistributionQuery
from .service import TimeDistributionService
from core.permitions import require_role

footfall_router = APIRouter(
    prefix="",
    tags=["footfall"],
    responses={404: {"description": "Not found"}},
)

time_distribution_service = TimeDistributionService()


@footfall_router.get("/time-distribution", response_model=TimeDistributionResponse)
async def get_time_distribution(
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    store_id: Optional[str] = Query(None, description="门店ID（可选）"),
    current_user = Depends(require_role(["operations_manager"], mode="in"))
):
    """获取时段客流分布
    
    - **start_date**: 开始日期 (YYYY-MM-DD)
    - **end_date**: 结束日期 (YYYY-MM-DD)
    - **store_id**: 门店ID（可选）
    """
    # 权限检查由require_role依赖处理
    
    try:
        # 验证时间范围
        from datetime import datetime
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        if start > end:
            raise HTTPException(status_code=400, detail="开始日期不能晚于结束日期")
        
        # 获取时间分布数据
        data = time_distribution_service.get_time_distribution(start_date, end_date, store_id)
        
        # 构建响应
        response = TimeDistributionResponse(
            data=data
        )
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取时段客流分布失败: {str(e)}")