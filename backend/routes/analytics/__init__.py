# Analytics routes module
from fastapi import APIRouter
from .footfall.routes import footfall_router

analytics_router = APIRouter(
    prefix="/analytics",
    tags=["analytics"],
    responses={404: {"description": "Not found"}},
)

analytics_router.include_router(footfall_router, prefix="/footfall")