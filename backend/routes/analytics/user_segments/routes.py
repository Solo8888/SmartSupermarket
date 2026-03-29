# User segments routes
# Provides API endpoints for user segments

from fastapi import APIRouter, HTTPException, Depends
from .schemas import UserSegmentsResponse
from .service import UserSegmentsService
from core.permitions import require_role

user_segments_router = APIRouter(
    prefix="",
    tags=["user_segments"],
    responses={404: {"description": "Not found"}},
)

user_segments_service = UserSegmentsService()


@user_segments_router.get("/user-segments", response_model=UserSegmentsResponse)
async def get_user_segments(
    current_user = Depends(require_role(["operations_manager"], mode="in"))
):
    """获取用户群体分类
    
    获取系统中所有的用户群体分类，包含群体ID、群体名称、用户数量和群体特征
    """
    try:
        segments_data = user_segments_service.get_user_segments()
        
        response = UserSegmentsResponse(
            segments=segments_data
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户群体分类失败: {str(e)}")
