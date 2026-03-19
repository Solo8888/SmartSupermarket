from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import get_db
from .schemas import (
    CartItemCreate, AddToCartResponse, CartResponse, CartItemResponse,
    RemoveCartItemResponse, RemoveCartItemsRequest
)
from .service import (
    add_item_to_cart, get_cart, remove_cart_item, remove_cart_items
)

cart_router = APIRouter(
    prefix="/api/cart",
    tags=["cart"],
    responses={404: {"description": "Not found"}},
)


@cart_router.post("/add", response_model=AddToCartResponse)
def add_to_cart(
    item: CartItemCreate,
    db: Session = Depends(get_db),
    # 这里可以添加用户身份验证依赖
    # current_user = Depends(get_current_user)
):
    """
    添加商品到购物车

    Args:
        item: 购物车项数据
        db: 数据库会话
        current_user: 当前用户（需要身份验证）

    Returns:
        添加结果和购物车信息
    """
    # 暂时使用固定用户ID，实际应用中应该从身份验证获取
    user_id = "12345678-1234-1234-1234-123456789012"

    try:
        cart = add_item_to_cart(db, user_id, item)

        # 构建响应数据
        cart_items = []
        for cart_item in cart.cart_items:
            cart_items.append(CartItemResponse(
                id=cart_item.id,
                cart_id=cart_item.cart_id,
                product_id=cart_item.product_id,
                product_name=cart_item.product_name,
                product_image=cart_item.product_image,
                price=cart_item.price,
                quantity=cart_item.quantity,
                created_at=cart_item.created_at,
                updated_at=cart_item.updated_at
            ))

        cart_response = CartResponse(
            id=cart.id,
            user_id=cart.user_id,
            items=cart_items,
            created_at=cart.created_at,
            updated_at=cart.updated_at
        )

        return AddToCartResponse(
            message="商品已成功添加到购物车",
            cart=cart_response
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@cart_router.get("/", response_model=CartResponse)
def get_user_cart(
    db: Session = Depends(get_db),
    # 这里可以添加用户身份验证依赖
    # current_user = Depends(get_current_user)
):
    """
    获取用户的购物车信息

    Args:
        db: 数据库会话
        current_user: 当前用户（需要身份验证）

    Returns:
        购物车信息
    """
    # 暂时使用固定用户ID，实际应用中应该从身份验证获取
    user_id = "12345678-1234-1234-1234-123456789012"

    try:
        cart = get_cart(db, user_id)

        # 构建响应数据
        cart_items = []
        for cart_item in cart.cart_items:
            cart_items.append(CartItemResponse(
                id=cart_item.id,
                cart_id=cart_item.cart_id,
                product_id=cart_item.product_id,
                product_name=cart_item.product_name,
                product_image=cart_item.product_image,
                price=cart_item.price,
                quantity=cart_item.quantity,
                created_at=cart_item.created_at,
                updated_at=cart_item.updated_at
            ))

        return CartResponse(
            id=cart.id,
            user_id=cart.user_id,
            items=cart_items,
            created_at=cart.created_at,
            updated_at=cart.updated_at
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@cart_router.delete("/items/{item_id}", response_model=RemoveCartItemResponse)
def remove_item(
    item_id: str,
    db: Session = Depends(get_db),
    # 这里可以添加用户身份验证依赖
    # current_user = Depends(get_current_user)
):
    """
    删除购物车中的单个商品

    Args:
        item_id: 购物车项ID
        db: 数据库会话
        current_user: 当前用户（需要身份验证）

    Returns:
        删除结果和更新后的购物车信息
    """
    # 暂时使用固定用户ID，实际应用中应该从身份验证获取
    user_id = "12345678-1234-1234-1234-123456789012"

    try:
        cart = remove_cart_item(db, user_id, item_id)

        # 构建响应数据
        cart_items = []
        for cart_item in cart.cart_items:
            cart_items.append(CartItemResponse(
                id=cart_item.id,
                cart_id=cart_item.cart_id,
                product_id=cart_item.product_id,
                product_name=cart_item.product_name,
                product_image=cart_item.product_image,
                price=cart_item.price,
                quantity=cart_item.quantity,
                created_at=cart_item.created_at,
                updated_at=cart_item.updated_at
            ))

        cart_response = CartResponse(
            id=cart.id,
            user_id=cart.user_id,
            items=cart_items,
            created_at=cart.created_at,
            updated_at=cart.updated_at
        )

        return RemoveCartItemResponse(
            message="商品已成功从购物车中删除",
            cart=cart_response
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@cart_router.post("/items/remove-many", response_model=RemoveCartItemResponse)
def remove_items(
    request: RemoveCartItemsRequest,
    db: Session = Depends(get_db),
    # 这里可以添加用户身份验证依赖
    # current_user = Depends(get_current_user)
):
    """
    删除购物车中的多个商品

    Args:
        request: 包含要删除的购物车项ID列表的请求体
        db: 数据库会话
        current_user: 当前用户（需要身份验证）

    Returns:
        删除结果和更新后的购物车信息
    """
    # 暂时使用固定用户ID，实际应用中应该从身份验证获取
    user_id = "12345678-1234-1234-1234-123456789012"

    try:
        cart = remove_cart_items(db, user_id, request.item_ids)

        # 构建响应数据
        cart_items = []
        for cart_item in cart.cart_items:
            cart_items.append(CartItemResponse(
                id=cart_item.id,
                cart_id=cart_item.cart_id,
                product_id=cart_item.product_id,
                product_name=cart_item.product_name,
                product_image=cart_item.product_image,
                price=cart_item.price,
                quantity=cart_item.quantity,
                created_at=cart_item.created_at,
                updated_at=cart_item.updated_at
            ))

        cart_response = CartResponse(
            id=cart.id,
            user_id=cart.user_id,
            items=cart_items,
            created_at=cart.created_at,
            updated_at=cart.updated_at
        )

        return RemoveCartItemResponse(
            message="商品已成功从购物车中删除",
            cart=cart_response
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
