

# 库存数据模型
# 定义库存相关的请求和响应数据模型

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class InventoryUpdate(BaseModel):
    """更新库存请求"""
    stock_quantity: Optional[int] = Field(None, description="库存数量", ge=0)
    warning_quantity: Optional[int] = Field(None, description="预警数量", ge=0)


class StockInRequest(BaseModel):
    """入库登记请求"""
    quantity: int = Field(..., description="入库数量", gt=0)
    remark: Optional[str] = Field(None, description="备注")


class StockOutRequest(BaseModel):
    """出库审核请求"""
    quantity: int = Field(..., description="出库数量", gt=0)
    remark: Optional[str] = Field(None, description="备注")


class InventoryResponse(BaseModel):
    """库存响应"""
    id: str
    product_id: str
    warehouse_id: int
    stock_quantity: int
    warning_quantity: int
    last_stock_time: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

