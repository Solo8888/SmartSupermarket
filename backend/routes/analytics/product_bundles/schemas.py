# Data models for product bundles analytics
from pydantic import BaseModel
from typing import List


class ProductBundle(BaseModel):
    """商品组合数据"""
    bundle_id: str
    products: List[str]
    expected_sales_increase: float


class ProductBundlesResponse(BaseModel):
    """商品组合响应"""
    bundles: List[ProductBundle]
