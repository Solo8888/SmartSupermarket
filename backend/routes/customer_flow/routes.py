# 客流数据路由
# 提供客流数据查询的API接口

from fastapi import APIRouter, HTTPException, Query
from datetime import datetime
from typing import Optional
from .schemas import CustomerFlowQuery, CustomerFlowListResponse
from .service import CustomerFlowService

customer_flow_router = APIRouter(
    prefix="/customer-flow",
    tags=["customer_flow"],
    responses={404: {"description": "Not found"}},
)

customer_flow_service = CustomerFlowService()


@customer_flow_router.get("/", response_model=CustomerFlowListResponse)
async def get_customer_flow(
    start_time: datetime = Query(..., description="开始时间"),
    end_time: datetime = Query(..., description="结束时间"),
    store_id: Optional[str] = Query(None, description="门店ID")
):
    """获取客流数据
    
    - **start_time**: 开始时间
    - **end_time**: 结束时间
    - **store_id**: 门店ID（可选）
    """
    try:
        # 验证时间范围
        if start_time > end_time:
            raise HTTPException(status_code=400, detail="开始时间不能晚于结束时间")
        
        # 获取客流数据
        data = customer_flow_service.get_customer_flow_data(start_time, end_time, store_id)
        
        # 构建响应
        response = CustomerFlowListResponse(
            data=data,
            total=len(data)
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取客流数据失败: {str(e)}")