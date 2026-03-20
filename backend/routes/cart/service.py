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
        raise BusinessException(
            f"商品不存在，ID: {item_data.product_id}",
            "PRODUCT_NOT_FOUND"
        )

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
            product_image=product.image_url,
            price=product.price,
            quantity=item_data.quantity
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)

    # 重新获取购物车，包含所有商品
    db.refresh(cart)
    return cart


def get_cart(db: Session, user_id: str) -> Cart:
    """
    获取用户的购物车

    Args:
        db: 数据库会话
        user_id: 用户ID

    Returns:
        购物车对象
    """
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        # 如果购物车不存在，创建一个空购物车
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


def remove_cart_item(db: Session, user_id: str, item_id: str) -> Cart:
    """
    删除购物车中的单个商品

    Args:
        db: 数据库会话
        user_id: 用户ID
        item_id: 购物车项ID

    Returns:
        更新后的购物车对象
    """
    # 获取用户购物车
    cart = get_cart(db, user_id)

    # 查找要删除的购物车项
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()

    if not cart_item:
        raise BusinessException(
            f"购物车项不存在，ID: {item_id}",
            "CART_ITEM_NOT_FOUND"
        )

    # 删除购物车项
    db.delete(cart_item)
    db.commit()

    # 重新获取购物车，包含所有商品
    db.refresh(cart)
    return cart


def remove_cart_items(db: Session, user_id: str, item_ids: list) -> Cart:
    """
    删除购物车中的多个商品

    Args:
        db: 数据库会话
        user_id: 用户ID
        item_ids: 购物车项ID列表

    Returns:
        更新后的购物车对象
    """
    # 获取用户购物车
    cart = get_cart(db, user_id)

    # 查找要删除的购物车项
    cart_items = db.query(CartItem).filter(
        CartItem.id.in_(item_ids),
        CartItem.cart_id == cart.id
    ).all()

    if not cart_items:
        raise BusinessException(
            "未找到要删除的购物车项",
            "CART_ITEMS_NOT_FOUND"
        )

    # 删除购物车项
    for item in cart_items:
        db.delete(item)
    db.commit()

    # 重新获取购物车，包含所有商品
    db.refresh(cart)
    return cart


def update_cart_item(
    db: Session, user_id: str, item_id: str, quantity: int
) -> Cart:
    """
    更新购物车商品数量

    Args:
        db: 数据库会话
        user_id: 用户ID
        item_id: 购物车项ID
        quantity: 新的数量

    Returns:
        更新后的购物车对象
    """
    # 获取用户购物车
    cart = get_cart(db, user_id)

    # 查找要更新的购物车项
    cart_item = db.query(CartItem).filter(
        CartItem.id == item_id,
        CartItem.cart_id == cart.id
    ).first()

    if not cart_item:
        raise BusinessException(
            f"购物车项不存在，ID: {item_id}",
            "CART_ITEM_NOT_FOUND"
        )

    # 更新数量
    cart_item.quantity = quantity
    db.commit()
    db.refresh(cart_item)

    # 重新获取购物车，包含所有商品
    db.refresh(cart)
    return cart
