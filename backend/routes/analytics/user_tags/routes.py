# User tags routes
# Provides API endpoints for user tags

from fastapi import APIRouter, HTTPException, Depends
from .schemas import UserTagsResponse
from .service import UserTagsService
from core.permitions import require_role

user_tags_router = APIRouter(
    prefix="",
    tags=["user_tags"],
    responses={404: {"description": "Not found"}},
)

user_tags_service = UserTagsService()


@user_tags_router.get("/user-tags", response_model=UserTagsResponse)
async def get_user_tags(
    current_user = Depends(require_role(["operations_manager"], mode="in"))
):
    """获取用户标签体系
    
    获取系统中所有的用户标签，包含标签ID、标签名称和权重
    """
    try:
        tags_data = user_tags_service.get_user_tags()
        
        response = UserTagsResponse(
            tags=tags_data
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户标签失败: {str(e)}")
