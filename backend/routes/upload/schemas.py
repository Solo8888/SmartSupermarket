# 上传数据模型
# 定义上传相关的请求和响应数据模型

from pydantic import BaseModel


class UploadResponse(BaseModel):
    """上传响应"""
    url: str
    filename: str
