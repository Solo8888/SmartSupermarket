"""API 路由模块"""
from .users.routes import user_router
from .category.routes import category_router
from .product.routes import product_router
from .upload.routes import upload_router
from .inventory.routes import inventory_router
from .promotion.routes import promotion_router
from .order.routes import order_router
from .store.routes import store_router
from .user_store.routes import user_store_router
from .cart.routes import cart_router
from .address_book.routes import address_router
from .review.routes import review_router
from .recommendations.routes import recommendation_router
from .customer_flow.routes import customer_flow_router

__all__ = [
    "user_router",
    "category_router",
    "product_router",
    "upload_router",
    "inventory_router",
    "promotion_router",
    "order_router",
    "store_router",
    "user_store_router",
    "cart_router",
    "address_router",
    "review_router",
    "recommendation_router",
    "customer_flow_router"
]
