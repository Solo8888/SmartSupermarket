# User segments schemas
# Define response models for user segments API

from pydantic import BaseModel
from typing import List


class UserSegment(BaseModel):
    """用户群体分类模型"""
    segment_id: str
    segment_name: str
    user_count: int
    characteristics: List[str]


class UserSegmentsResponse(BaseModel):
    """用户群体分类响应模型"""
    segments: List[UserSegment]
