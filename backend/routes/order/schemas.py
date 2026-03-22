# 订单数据模型
# 定义订单相关的请求和响应数据模型

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class OrderItemCreate(BaseModel):
    """创建订单项请求"""
    product_id: str = Field(..., description="商品ID")
    quantity: int = Field(..., description="购买数量", gt=0)


class OrderCreate(BaseModel):
    """创建订单请求"""
    items: List[OrderItemCreate] = Field(..., description="订单项列表")
    address_id: Optional[str] = Field(None, description="地址簿中的地址ID")
    shipping_address: Optional[str] = Field(None, description="收货地址")
    contact_name: Optional[str] = Field(None, description="联系人姓名", max_length=50)
    contact_phone: Optional[str] = Field(None, description="联系电话", max_length=20)
    remark: Optional[str] = Field(None, description="备注")


class OrderItemResponse(BaseModel):
    """订单项响应"""
    id: str
    order_id: str
    product_id: Optional[str] = None
    product_name: str
    product_image: Optional[str] = None
    price: Decimal
    quantity: int
    subtotal: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    """订单响应"""
    id: str
    order_no: str
    user_id: Optional[str] = None
    total_amount: Decimal
    discount_amount: Decimal
    final_amount: Decimal
    status: str
    payment_method: Optional[str] = None
    payment_time: Optional[datetime] = None
    shipping_address: Optional[str] = None
    contact_name: Optional[str] = None
    contact_phone: Optional[str] = None
    remark: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    items: Optional[List[OrderItemResponse]] = None

    class Config:
        from_attributes = True


class OrderUpdateStatus(BaseModel):
    """更新订单状态请求"""
    status: str = Field(..., description="订单状态", pattern="^(pending|paid|shipped|completed|cancelled|refunded)$")


class OrderPay(BaseModel):
    """支付订单请求"""
    payment_method: str = Field(..., description="支付方式", pattern="^(alipay|wechat|mock)$")
