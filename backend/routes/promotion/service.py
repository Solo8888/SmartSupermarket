# 促销活动服务
# 处理促销活动相关的业务逻辑

from sqlalchemy.orm import Session
from models.promotion import Promotion
from .schemas import PromotionCreate
from sqlalchemy import func


class PromotionService:
    @staticmethod
    def create_promotion(db: Session, payload: PromotionCreate, user) -> dict:
        """
        创建促销活动

        Args:
            db: 数据库会话
            payload: 创建促销活动请求体
            user: 当前用户

        Returns:
            创建成功的促销活动信息
        """
        # 验证时间逻辑
        if payload.start_time >= payload.end_time:
            raise ValueError("开始时间必须早于结束时间")

        # 创建新促销活动
        promotion = Promotion(
            name=payload.name,
            description=payload.description,
            type=payload.type,
            value=payload.value,
            start_time=payload.start_time,
            end_time=payload.end_time,
            status=payload.status
        )

        db.add(promotion)
        db.commit()
        db.refresh(promotion)

        # 转换为字典返回
        return {
            "id": promotion.id,
            "name": promotion.name,
            "description": promotion.description,
            "type": promotion.type,
            "value": promotion.value,
            "start_time": promotion.start_time,
            "end_time": promotion.end_time,
            "status": promotion.status,
            "created_at": promotion.created_at,
            "updated_at": promotion.updated_at
        }
