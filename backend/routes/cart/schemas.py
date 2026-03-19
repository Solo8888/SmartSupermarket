from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class CartItemBase(BaseModel):
    product_id: str = Field(..., description="商品ID")
    quantity: int = Field(..., gt=0, description="购买数量")


class CartItemCreate(CartItemBase):
    pass


class CartItemResponse(BaseModel):
    id: str
    cart_id: str
    product_id: str
    product_name: str
    product_image: Optional[str] = None
    price: Decimal
    quantity: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    id: str
    user_id: str
    items: List[CartItemResponse] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AddToCartResponse(BaseModel):
    message: str
    cart: CartResponse


class RemoveCartItemResponse(BaseModel):
    message: str
    cart: CartResponse
