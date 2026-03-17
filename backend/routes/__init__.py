"""API 路由模块"""
from .auth.routes import auth_router
from .category.routes import category_router
from .product.routes import product_router
from .upload.routes import upload_router
from .inventory.routes import inventory_router
from .promotion.routes import promotion_router
from .order.routes import order_router
from .store.routes import store_router
from .user_store.routes import user_store_router
from .user.routes import user_router

__all__ = [
    "auth_router",
    "category_router",
    "product_router",
    "upload_router",
    "inventory_router",
    "promotion_router",
    "order_router",
    "store_router",
    "user_store_router",
    "user_router"
]
