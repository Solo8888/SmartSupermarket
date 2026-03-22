from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import get_db
from core.auth import get_current_user_id
from .schemas import (
    CartItemCreate, AddToCartResponse, CartResponse, CartItemResponse,
    RemoveCartItemResponse, RemoveCartItemsRequest, CartItemUpdate
)
from .service import (
    add_item_to_cart, get_cart, remove_cart_item, remove_cart_items, update_cart_item, clear_cart
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
    current_user_id: str = Depends(get_current_user_id)
):
    user_id = current_user_id

    try:
        cart = add_item_to_cart(db, user_id, item)

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


@cart_router.get("", response_model=CartResponse)
def get_user_cart(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    user_id = current_user_id

    try:
        cart = get_cart(db, user_id)

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
    current_user_id: str = Depends(get_current_user_id)
):
    user_id = current_user_id

    try:
        cart = remove_cart_item(db, user_id, item_id)

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


@cart_router.put("/items/{item_id}", response_model=RemoveCartItemResponse)
def update_item(
    item_id: str,
    item_update: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    user_id = current_user_id

    try:
        cart = update_cart_item(db, user_id, item_id, item_update.quantity)

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
            message="商品数量已更新",
            cart=cart_response
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@cart_router.post("/items/remove-many", response_model=RemoveCartItemResponse)
def remove_items(
    request: RemoveCartItemsRequest,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    user_id = current_user_id

    try:
        cart = remove_cart_items(db, user_id, request.item_ids)

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


@cart_router.delete("", response_model=RemoveCartItemResponse)
def clear_user_cart(
    db: Session = Depends(get_db),
    current_user_id: str = Depends(get_current_user_id)
):
    user_id = current_user_id

    try:
        cart = clear_cart(db, user_id)

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
            message="购物车已清空",
            cart=cart_response
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
