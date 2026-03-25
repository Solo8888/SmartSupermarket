from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends
from models import get_db, User
from core.permitions import require_role

from .schemas import CustomerFlowHourlyRequest, CustomerFlowHourlyResponse
from .service import CustomerFlowService

# 创建客流分析路由器
customer_flow_router = APIRouter(prefix='/customer-flow', tags=['customer_flow'])


@customer_flow_router.post('/hourly', response_model=CustomerFlowHourlyResponse)
async def get_hourly_customer_flow(
    request: CustomerFlowHourlyRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_role('operations_manager'))
):
    """
    获取各时段客流分布接口

    Args:
        request: 获取各时段客流分布请求体
        db: 数据库会话
        user: 当前用户

    Returns:
        各时段客流分布响应
    """
    hourly_data = CustomerFlowService.get_hourly_customer_flow(
        db, str(request.store_id), request.start_date, request.end_date
    )
    
    return CustomerFlowHourlyResponse(
        store_id=request.store_id,
        start_date=request.start_date,
        end_date=request.end_date,
        data=hourly_data
    )
