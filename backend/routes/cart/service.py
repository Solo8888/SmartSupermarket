from sqlalchemy.orm import Session
from models import Cart, CartItem, Product
from core.exceptions import BusinessException
from .schemas import CartItemCreate


def get_or_create_cart(db: Session, user_id: str) -> Cart:
    """
    获取或创建用户的购物车

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        购物车对象
    """
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def add_item_to_cart(
    db: Session, user_id: str, item_data: CartItemCreate
) -> Cart:
    """
    添加商品到购物车

    Args:
        db: 数据库会话
        user_id: 用户ID
        item_data: 购物车项数据

    Returns:
        更新后的购物车对象
    """
    # 获取或创建购物车
    cart = get_or_create_cart(db, user_id)

    # 检查商品是否存在
    product = db.query(Product).filter(
        Product.id == item_data.product_id
    ).first()
    if not product:
        raise BusinessException(f"商品不存在，ID: {item_data.product_id}")

    # 检查商品是否已在购物车中
    existing_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == item_data.product_id
    ).first()

    if existing_item:
        # 更新数量
        existing_item.quantity += item_data.quantity
        db.commit()
        db.refresh(existing_item)
    else:
        # 创建新的购物车项
        new_item = CartItem(
            cart_id=cart.id,
            product_id=product.id,
            product_name=product.name,
            product_image=product.image,
            price=product.price,
            quantity=item_data.quantity
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)

    # 重新获取购物车，包含所有商品
    db.refresh(cart)
    return cart
