# 评价服务
# 处理评价相关的业务逻辑

from sqlalchemy.orm import Session
from models.review import Review
from models.order import Order, OrderItem
from models.product import Product
from .schemas import ReviewCreate
from core.exceptions import NotFoundError
from sqlalchemy import func
from datetime import datetime, timedelta
import uuid


class ReviewService:
    @staticmethod
    def create_review(db: Session, payload: ReviewCreate, user) -> dict:
        """
        创建评价

        Args:
            db: 数据库会话
            payload: 创建评价请求体
            user: 当前用户

        Returns:
            创建成功的评价信息

        Raises:
            NotFoundError: 订单项不存在或不属于当前用户
        """
        # 查询订单项
        order_item = db.query(OrderItem).filter(OrderItem.id == payload.order_item_id).first()
        if not order_item:
            raise NotFoundError("订单项不存在")

        # 查询订单
        order = db.query(Order).filter(Order.id == order_item.order_id).first()
        if not order:
            raise NotFoundError("订单不存在")

        # 验证订单是否属于当前用户
        if order.user_id != user.id:
            raise NotFoundError("无权操作此订单")

        # 验证订单状态是否为已收货
        if order.status != 'delivered':
            raise ValueError("只有已收货的订单才能评价")

        # 检查是否已经评价过
        existing_review = db.query(Review).filter(
            Review.order_item_id == payload.order_item_id
        ).first()
        if existing_review:
            raise ValueError("此商品已经评价过")

        # 创建评价
        review = Review(
            order_id=order.id,
            order_item_id=order_item.id,
            user_id=user.id,
            product_id=order_item.product_id,
            rating=payload.rating,
            content=payload.content
        )

        db.add(review)
        db.commit()
        db.refresh(review)

        # 更新订单状态为已完成
        order.status = 'completed'
        db.commit()

        # 转换为字典返回
        return {
            "id": review.id,
            "order_id": review.order_id,
            "order_item_id": review.order_item_id,
            "user_id": review.user_id,
            "product_id": review.product_id,
            "rating": review.rating,
            "content": review.content,
            "created_at": review.created_at
        }

    @staticmethod
    def get_reviews_by_product(db: Session, product_id: str, page: int = 1, size: int = 10) -> dict:
        """
        获取商品的评价列表（分页）

        Args:
            db: 数据库会话
            product_id: 商品ID
            page: 页码
            size: 每页数量

        Returns:
            评价列表（分页）
        """
        # 查询商品是否存在
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise NotFoundError("商品不存在")

        # 查询评价
        query = db.query(Review).filter(Review.product_id == product_id)
        total = query.count()

        # 分页查询
        offset = (page - 1) * size
        reviews = query.order_by(Review.created_at.desc()).offset(offset).limit(size).all()

        # 转换为字典列表
        reviews_dict = []
        for review in reviews:
            reviews_dict.append({
                "id": review.id,
                "order_id": review.order_id,
                "order_item_id": review.order_item_id,
                "user_id": review.user_id,
                "product_id": review.product_id,
                "rating": review.rating,
                "content": review.content,
                "created_at": review.created_at
            })

        return {
            "items": reviews_dict,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }

    @staticmethod
    def get_reviews_by_user(db: Session, user_id: str, page: int = 1, size: int = 10) -> dict:
        """
        获取用户的评价列表（分页）

        Args:
            db: 数据库会话
            user_id: 用户ID
            page: 页码
            size: 每页数量

        Returns:
            评价列表（分页）
        """
        # 查询评价
        query = db.query(Review).filter(Review.user_id == user_id)
        total = query.count()

        # 分页查询
        offset = (page - 1) * size
        reviews = query.order_by(Review.created_at.desc()).offset(offset).limit(size).all()

        # 转换为字典列表
        reviews_dict = []
        for review in reviews:
            reviews_dict.append({
                "id": review.id,
                "order_id": review.order_id,
                "order_item_id": review.order_item_id,
                "user_id": review.user_id,
                "product_id": review.product_id,
                "rating": review.rating,
                "content": review.content,
                "created_at": review.created_at
            })

        return {
            "items": reviews_dict,
            "total": total,
            "page": page,
            "size": size,
            "pages": (total + size - 1) // size
        }

    @staticmethod
    def auto_review(db: Session):
        """
        自动评价：7天未评价的已收货订单默认好评

        Args:
            db: 数据库会话
        """
        # 计算7天前的日期
        seven_days_ago = datetime.now() - timedelta(days=7)

        # 查询7天前已收货但未评价的订单项
        order_items = db.query(OrderItem).join(Order).filter(
            Order.status == 'delivered',
            Order.updated_at < seven_days_ago
        ).all()

        for order_item in order_items:
            # 检查是否已经评价过
            existing_review = db.query(Review).filter(
                Review.order_item_id == order_item.id
            ).first()
            if not existing_review:
                # 创建默认好评
                review = Review(
                    order_id=order_item.order_id,
                    order_item_id=order_item.id,
                    user_id=order_item.order.user_id,
                    product_id=order_item.product_id,
                    rating=5,  # 默认5星好评
                    content="默认好评"
                )
                db.add(review)

                # 更新订单状态为已完成
                order_item.order.status = 'completed'

        db.commit()
