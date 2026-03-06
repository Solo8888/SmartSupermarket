# 上传API路由
# 提供文件上传接口

from fastapi import APIRouter, UploadFile, File
from .schemas import UploadResponse
from .service import UploadService

upload_router = APIRouter(prefix='/upload', tags=['upload'])


@upload_router.post('/image', response_model=UploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """
    上传图片接口

    Args:
        file: 上传的图片文件

    Returns:
        上传后的图片信息
    """
    result = await UploadService.upload_image(file)
    return UploadResponse(**result)
