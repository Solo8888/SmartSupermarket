# Analytics routes module
from fastapi import APIRouter
from .footfall.routes import footfall_router
from .association_rules.routes import association_rules_router
from .product_bundles.routes import product_bundles_router
from .user_tags.routes import user_tags_router

analytics_router = APIRouter(
    prefix="/analytics",
    responses={404: {"description": "Not found"}},
)

analytics_router.include_router(footfall_router, prefix="/footfall")
analytics_router.include_router(association_rules_router)
analytics_router.include_router(product_bundles_router)
analytics_router.include_router(user_tags_router)