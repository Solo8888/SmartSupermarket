from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from models import get_db
from core.permitions import require_role
from .schemas import AssociationRulesResponse
from .service import AssociationRulesService

association_rules_router = APIRouter(
    prefix="",
    tags=["association_rules"],
    responses={404: {"description": "Not found"}},
)

association_rules_service = AssociationRulesService()


@association_rules_router.get("/association-rules", response_model=AssociationRulesResponse)
async def get_association_rules(
    start_date: str = Query(..., description="开始日期 (YYYY-MM-DD)"),
    end_date: str = Query(..., description="结束日期 (YYYY-MM-DD)"),
    min_support: float = Query(0.01, description="最小支持度 (0-1)"),
    min_confidence: float = Query(0.5, description="最小置信度 (0-1)"),
    current_user = Depends(require_role(["operations_manager"], mode="in")),
    db: Session = Depends(get_db)
):
    """获取商品关联规则
    
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
        
        data = association_rules_service.get_association_rules(
            db, start_date, end_date, min_support, min_confidence
        )
        
        return data
    except HTTPException:
        raise
    except ValueError as e:
        if "does not match format" in str(e):
            raise HTTPException(status_code=400, detail=f"日期格式错误: {str(e)}")
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取关联规则失败: {str(e)}")
