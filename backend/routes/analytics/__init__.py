# Analytics routes module
from fastapi import APIRouter
from .footfall.routes import footfall_router
from .association_rules.routes import association_rules_router

analytics_router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    responses={404: {"description": "Not found"}},
)

analytics_router.include_router(footfall_router, prefix="/footfall")
analytics_router.include_router(association_rules_router)