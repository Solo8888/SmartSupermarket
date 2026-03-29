# User segments schemas
# Define response models for user segments API

from pydantic import BaseModel
from typing import List, Dict, Any


class UserSegment(BaseModel):
    """用户群体分类模型"""
    segment_id: str
    segment_name: str
    user_count: int
    characteristics: List[str]


class UserSegmentsResponse(BaseModel):
    """用户群体分类响应模型"""
    segments: List[UserSegment]


class UserSegmentDetail(BaseModel):
    """用户群体详情模型"""
    segment_id: str
    segment_name: str
    users: List[Any]
    tag_distribution: List[Any]
    behavior_analysis: Dict[str, Any]
