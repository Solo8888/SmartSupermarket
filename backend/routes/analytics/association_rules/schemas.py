# Data models for association rules analytics
from pydantic import BaseModel
from typing import List


class AssociationRule(BaseModel):
    """关联规则数据"""
    rule_id: str
    antecedent: List[str]
    consequent: List[str]
    support: float
    confidence: float


class AssociationRulesResponse(BaseModel):
    """关联规则响应"""
    rules: List[AssociationRule]
