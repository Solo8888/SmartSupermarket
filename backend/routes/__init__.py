"""API 路由模块"""
from .auth.routes import auth_router
from .category.routes import category_router
from .product.routes import product_router
from .upload.routes import upload_router
from .inventory.routes import inventory_router

__all__ = [
    "auth_router",
    "category_router",
    "product_router",
    "upload_router",
    "inventory_router"
]
