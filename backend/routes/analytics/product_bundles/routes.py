from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from models import get_db
from core.permitions import require_role
from .schemas import ProductBundlesResponse
from .service import ProductBundlesService

product_bundles_router = APIRouter(
    prefix="",
    tags=["product_bundles"],
    responses={404: {"description": "Not found"}},
)

product_bundles_service = ProductBundlesService()


@product_bundles_router.get("/product-bundles", response_model=ProductBundlesResponse)
async def get_product_bundles(
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    min_support: float = Query(0.01, description="最小支持度 (0-1)"),
    min_confidence: float = Query(0.5, description="最小置信度 (0-1)"),
    current_user = Depends(require_role(["operations_manager"], mode="in")),
    db: Session = Depends(get_db)
):
    """获取商品组合
    
    - **start_date**: 开始日期 (YYYY-MM-DD)
    - **end_date**: 结束日期 (YYYY-MM-DD)
    - **min_support**: 最小支持度 (0-1)
    - **min_confidence**: 最小置信度 (0-1)
    """
    try:
        from datetime import datetime
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        
        if start > end:
            raise HTTPException(status_code=400, detail="开始日期不能晚于结束日期")
        
        if min_support < 0 or min_support > 1:
            raise HTTPException(status_code=400, detail="min_support 必须在 0-1 范围内")
        
        if min_confidence < 0 or min_confidence > 1:
            raise HTTPException(status_code=400, detail="min_confidence 必须在 0-1 范围内")
        
        data = product_bundles_service.get_product_bundles(
            db, start_date, end_date, min_support, min_confidence
        )
        
        return data
    except ValueError as e:
        if "does not match format" in str(e):
            raise HTTPException(status_code=400, detail=f"日期格式错误: {str(e)}")
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取商品组合失败: {str(e)}")
