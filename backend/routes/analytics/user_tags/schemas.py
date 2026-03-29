# User tags schemas
# Define response models for user tags API

from pydantic import BaseModel
from typing import List


class UserTag(BaseModel):
    """用户标签模型"""
    tag_id: str
    tag_name: str
    weight: float


class UserTagsResponse(BaseModel):
    """用户标签响应模型"""
    tags: List[UserTag]
