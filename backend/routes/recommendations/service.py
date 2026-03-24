# 推荐系统服务
# 处理个性化商品推荐的业务逻辑

from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from models.product import Product
from models.inventory import Inventory
from models.order import Order, OrderItem
from models.review import Review
from models.promotion import Promotion
from models.promotion_product import PromotionProduct
from .schemas import RecommendationRequest
from core.exceptions import NotFoundError


class RecommendationService:
    @staticmethod
    def is_new_user(db: Session, user_id: str) -> bool:
        """
        判断用户是否为新用户（无购买历史）

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            bool: 是否为新用户
        """
        order_count = db.query(Order).filter(Order.user_id == user_id).count()
        return order_count == 0

    @staticmethod
    def get_user_preferred_categories(db: Session, user_id: str) -> list:
        """
        获取用户偏好的商品分类

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            list: 分类ID列表，按偏好程度排序
        """
        # 查询用户购买过的商品分类及购买次数
        category_counts = db.query(
            Product.category_id,
            func.count(OrderItem.id).label('count')
        ).join(
            OrderItem, Product.id == OrderItem.product_id
        ).join(
            Order, OrderItem.order_id == Order.id
        ).filter(
            Order.user_id == user_id
        ).group_by(
            Product.category_id
        ).order_by(
            desc('count')
        ).all()

        return [category_id for category_id, _ in category_counts]

    @staticmethod
    def calculate_product_score(db: Session, product_id: str, user_id: str = None) -> tuple:
        """
        计算商品的推荐分数

        Args:
            db: 数据库会话
            product_id: 商品ID
            user_id: 用户ID（可选）

        Returns:
            tuple: (分数, 推荐理由)
        """
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            return 0.0, "商品不存在"

        # 基础分数计算
        score = 0.0
        reasons = []

        # 1. 销量分数（权重0.3）
        sales_score = min(product.sales_count / 100.0, 1.0) * 0.3
        score += sales_score
        if product.sales_count > 50:
            reasons.append("热销商品")

        # 2. 浏览量分数（权重0.2）
        view_score = min(product.view_count / 200.0, 1.0) * 0.2
        score += view_score
        if product.view_count > 100:
            reasons.append("高人气商品")

        # 3. 库存分数（权重0.2）
        inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
        stock = inventory.stock_quantity if inventory else 0
        stock_score = min(stock / 100.0, 1.0) * 0.2
        score += stock_score

        # 4. 促销分数（权重0.3）
        promotion_count = db.query(PromotionProduct).filter(
            PromotionProduct.product_id == product_id
        ).join(
            Promotion, PromotionProduct.promotion_id == Promotion.id
        ).filter(
            Promotion.status == 'active'
        ).count()
        if promotion_count > 0:
            score += 0.3
            reasons.append("促销商品")

        # 5. 用户偏好分数（如果提供了用户ID）
        if user_id:
            preferred_categories = RecommendationService.get_user_preferred_categories(db, user_id)
            if product.category_id in preferred_categories:
                # 偏好分类的商品加分
                score += 0.2
                reasons.append("您可能喜欢的分类")

        # 生成推荐理由
        if not reasons:
            reasons.append("优质商品")

        return score, "，".join(reasons)

    @staticmethod
    def get_personalized_recommendations(db: Session, user, request: RecommendationRequest) -> dict:
        """
        获取个性化商品推荐

        Args:
            db: 数据库会话
            user: 当前用户
            request: 推荐请求参数

        Returns:
            dict: 推荐结果
        """
        # 构建基础查询，关联库存表
        query = db.query(Product, Inventory.stock_quantity).outerjoin(
            Inventory, Product.id == Inventory.product_id
        ).filter(
            Product.status == 'active'
        )

        # 门店过滤
        if request.store_id:
            query = query.filter(Product.store_id == request.store_id)
        # 系统管理员和顾客可以查看所有商品，其他用户只能查看关联门店的商品
        elif user and user.role not in ['system_admin', 'customer']:
            from models.user_store import UserStore
            user_stores = db.query(UserStore).filter(UserStore.user_id == user.id).all()
            user_store_ids = [user_store.store_id for user_store in user_stores]
            if user_store_ids:
                query = query.filter(Product.store_id.in_(user_store_ids))
            else:
                # 如果用户没有关联门店，返回空列表
                return {
                    "products": [],
                    "total": 0,
                    "algorithm": "personalized",
                    "explanation": "用户未分配门店，无法推荐商品"
                }

        # 执行查询
        products_with_stock = query.all()

        # 计算每个商品的推荐分数
        scored_products = []
        for product, stock_quantity in products_with_stock:
            # 过滤掉库存为0的商品
            if stock_quantity and stock_quantity > 0:
                score, reason = RecommendationService.calculate_product_score(db, product.id, user.id if user else None)
                scored_products.append({
                    "id": product.id,
                    "name": product.name,
                    "category_id": product.category_id,
                    "store_id": product.store_id,
                    "price": product.price,
                    "original_price": product.original_price,
                    "description": product.description,
                    "image_url": product.image_url,
                    "stock": stock_quantity or 0,
                    "sales_count": product.sales_count,
                    "view_count": product.view_count,
                    "score": score,
                    "reason": reason
                })

        # 按分数排序
        scored_products.sort(key=lambda x: x['score'], reverse=True)

        # 限制推荐数量
        recommended_products = scored_products[:request.limit]

        # 确定使用的算法
        algorithm = "new_user" if user and RecommendationService.is_new_user(db, user.id) else "personalized"
        explanation = "基于热门商品、促销活动和库存情况的综合推荐" if algorithm == "new_user" else "基于用户历史行为和商品热度的个性化推荐"

        return {
            "products": recommended_products,
            "total": len(recommended_products),
            "algorithm": algorithm,
            "explanation": explanation
        }

    @staticmethod
    def get_new_user_recommendations(db: Session, request: RecommendationRequest) -> dict:
        """
        获取新用户推荐（无用户信息时使用）

        Args:
            db: 数据库会话
            request: 推荐请求参数

        Returns:
            dict: 推荐结果
        """
        # 构建基础查询，关联库存表
        query = db.query(Product, Inventory.stock_quantity).outerjoin(
            Inventory, Product.id == Inventory.product_id
        ).filter(
            Product.status == 'active'
        )

        # 门店过滤
        if request.store_id:
            query = query.filter(Product.store_id == request.store_id)

        # 执行查询
        products_with_stock = query.all()

        # 计算每个商品的推荐分数（不考虑用户偏好）
        scored_products = []
        for product, stock_quantity in products_with_stock:
            # 过滤掉库存为0的商品
            if stock_quantity and stock_quantity > 0:
                score, reason = RecommendationService.calculate_product_score(db, product.id)
                scored_products.append({
                    "id": product.id,
                    "name": product.name,
                    "category_id": product.category_id,
                    "store_id": product.store_id,
                    "price": product.price,
                    "original_price": product.original_price,
                    "description": product.description,
                    "image_url": product.image_url,
                    "stock": stock_quantity or 0,
                    "sales_count": product.sales_count,
                    "view_count": product.view_count,
                    "score": score,
                    "reason": reason
                })

        # 按分数排序
        scored_products.sort(key=lambda x: x['score'], reverse=True)

        # 限制推荐数量
        recommended_products = scored_products[:request.limit]

        return {
            "products": recommended_products,
            "total": len(recommended_products),
            "algorithm": "new_user",
            "explanation": "基于热门商品、促销活动和库存情况的综合推荐"
        }