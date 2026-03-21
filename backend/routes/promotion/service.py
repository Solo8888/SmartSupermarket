# 促销活动服务
# 处理促销活动相关的业务逻辑

from fastapi_pagination import Page, Params
from fastapi_pagination.ext.sqlalchemy import paginate as sqlalchemy_paginate
from sqlalchemy import func
from sqlalchemy.orm import Session

from core.exceptions import NotFoundError
from models.promotion import Promotion
from .schemas import PromotionCreate


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

    @staticmethod
    def get_promotions(db: Session, params: Params) -> Page[Promotion]:
        """
        获取促销活动列表

        Args:
            db: 数据库会话
            params: 分页参数

        Returns:
            促销活动列表（分页）
        """
        query = db.query(Promotion).order_by(Promotion.created_at.desc())
        return sqlalchemy_paginate(query, params=params)

    @staticmethod
    def get_promotion(db: Session, promotion_id: str) -> dict:
        """
        获取单个促销活动详情

        Args:
            db: 数据库会话
            promotion_id: 促销活动ID

        Returns:
            促销活动详情

        Raises:
            NotFoundError: 促销活动不存在
        """
        promotion = db.query(Promotion).filter(Promotion.id == promotion_id).first()
        if not promotion:
            raise NotFoundError("促销活动不存在")

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

    @staticmethod
    def update_promotion(db: Session, promotion_id: str, payload, user) -> dict:
        """
        更新促销活动

        Args:
            db: 数据库会话
            promotion_id: 促销活动ID
            payload: 更新促销活动请求体
            user: 当前用户

        Returns:
            更新成功的促销活动信息

        Raises:
            NotFoundError: 促销活动不存在
        """

        # 获取促销活动
        promotion = db.query(Promotion).filter(Promotion.id == promotion_id).first()
        if not promotion:
            raise NotFoundError("促销活动不存在")

        # 验证时间逻辑（如果提供了start_time或end_time）
        start_time = payload.start_time if payload.start_time is not None else promotion.start_time
        end_time = payload.end_time if payload.end_time is not None else promotion.end_time
        if start_time >= end_time:
            raise ValueError("开始时间必须早于结束时间")

        # 更新字段（只更新提供的字段）
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(promotion, field, value)

        # 更新时间戳
        promotion.updated_at = func.current_timestamp()

        db.commit()
        db.refresh(promotion)

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

    @staticmethod
    def delete_promotion(db: Session, promotion_id: str, user) -> None:
        """
        删除促销活动

        Args:
            db: 数据库会话
            promotion_id: 促销活动ID
            user: 当前用户

        Raises:
            NotFoundError: 促销活动不存在
        """
        # 获取促销活动
        promotion = db.query(Promotion).filter(Promotion.id == promotion_id).first()
        if not promotion:
            raise NotFoundError("促销活动不存在")

        # 删除促销活动
        db.delete(promotion)
        db.commit()
