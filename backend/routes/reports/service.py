# Reports service
# Implement business logic for reports

from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
from .schemas import RecommendationConversionRequest, RecommendationConversionResponse, RecommendationConversionMetrics, RecommendationConversionTrend, RecommendationConversionDetail
from models.product import Product
from models.order import Order, OrderItem
from models.cart import Cart, CartItem

# 简单的内存缓存
_cache = {}
_CACHE_TTL = 3600  # 缓存过期时间（秒）


class ReportsService:
    @staticmethod
    def _get_cache_key(request: RecommendationConversionRequest) -> str:
        """
        生成缓存键

        Args:
            request: 分析请求参数

        Returns:
            str: 缓存键
        """
        parts = [
            f"start_date={request.start_date or 'None'}",
            f"end_date={request.end_date or 'None'}",
            f"store_id={request.store_id or 'None'}",
            f"category_id={request.category_id or 'None'}",
            f"time_granularity={request.time_granularity}",
            f"include_details={request.include_details}"
        ]
        return "|".join(parts)

    @staticmethod
    def _get_from_cache(key: str) -> Optional[Dict[str, Any]]:
        """
        从缓存获取数据

        Args:
            key: 缓存键

        Returns:
            Optional[Dict]: 缓存的数据
        """
        if key in _cache:
            cached_data = _cache[key]
            if datetime.now().timestamp() - cached_data['timestamp'] < _CACHE_TTL:
                return cached_data['data']
            else:
                del _cache[key]
        return None

    @staticmethod
    def _set_to_cache(key: str, data: Dict[str, Any]) -> None:
        """
        设置缓存数据

        Args:
            key: 缓存键
            data: 要缓存的数据
        """
        _cache[key] = {
            'data': data,
            'timestamp': datetime.now().timestamp()
        }

    @staticmethod
    def get_recommendation_conversion(db: Session, request: RecommendationConversionRequest) -> Dict[str, Any]:
        """
        获取推荐转化率分析数据

        Args:
            db: 数据库会话
            request: 分析请求参数

        Returns:
            Dict: 分析结果
        """
        # 生成缓存键
        cache_key = ReportsService._get_cache_key(request)
        
        # 尝试从缓存获取数据
        cached_data = ReportsService._get_from_cache(cache_key)
        if cached_data:
            return cached_data

        # 处理日期范围
        end_date = request.end_date or date.today()
        start_date = request.start_date or (end_date - timedelta(days=30))

        # 构建基础查询过滤器
        filters = {
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }

        if request.store_id:
            filters['store_id'] = request.store_id
        if request.category_id:
            filters['category_id'] = request.category_id

        # 模拟推荐数据（基于现有订单和购物车数据）
        # 注意：实际生产环境中应该有专门的推荐记录表格
        recommendation_data = ReportsService._generate_mock_recommendation_data(db, start_date, end_date, request.store_id, request.category_id)

        # 计算汇总指标
        summary_metrics = ReportsService._calculate_metrics(recommendation_data)

        # 生成趋势数据
        trends = []
        if request.time_granularity:
            trends = ReportsService._generate_trends(recommendation_data, start_date, end_date, request.time_granularity)

        # 生成详细数据
        details = []
        if request.include_details:
            details = ReportsService._generate_details(recommendation_data)

        result = {
            "summary": summary_metrics,
            "trends": trends,
            "details": details,
            "filters": filters
        }

        # 存入缓存
        ReportsService._set_to_cache(cache_key, result)

        return result

    @staticmethod
    def _generate_mock_recommendation_data(db: Session, start_date: date, end_date: date, store_id: Optional[str], category_id: Optional[str]) -> List[Dict[str, Any]]:
        """
        生成模拟的推荐数据（基于现有订单和购物车数据）

        Args:
            db: 数据库会话
            start_date: 开始日期
            end_date: 结束日期
            store_id: 门店ID
            category_id: 分类ID

        Returns:
            List[Dict]: 推荐数据列表
        """
        recommendation_data = []

        # 查询商品数据
        product_query = db.query(Product)
        if category_id:
            product_query = product_query.filter(Product.category_id == category_id)
        
        products = product_query.all()

        # 查询订单数据
        order_query = db.query(Order, OrderItem).join(OrderItem).filter(
            Order.created_at >= start_date,
            Order.created_at <= end_date
        )
        orders = order_query.all()

        # 查询购物车数据
        cart_query = db.query(CartItem).join(Cart).filter(
            Cart.created_at >= start_date,
            Cart.created_at <= end_date
        )
        carts = cart_query.all()

        # 生成推荐记录
        recommendation_id = 1
        for product in products:
            # 模拟推荐展示
            recommendation = {
                "recommendation_id": f"rec_{recommendation_id}",
                "user_id": f"user_{(recommendation_id % 10) + 1}",
                "product_id": product.id,
                "product_name": product.name,
                "store_id": product.store_id if hasattr(product, 'store_id') else "store_1",
                "category_id": product.category_id,
                "recommended_at": datetime.now() - timedelta(days=recommendation_id % 30),
                "clicked_at": None,
                "added_to_cart_at": None,
                "purchased_at": None,
                "status": "impression"
            }

            # 检查是否有点击行为（模拟30%的点击率）
            if recommendation_id % 3 == 0:
                recommendation["clicked_at"] = recommendation["recommended_at"] + timedelta(hours=1)
                recommendation["status"] = "click"

                # 检查是否有加购行为（模拟20%的加购率）
                if recommendation_id % 5 == 0:
                    recommendation["added_to_cart_at"] = recommendation["clicked_at"] + timedelta(hours=2)
                    recommendation["status"] = "add_to_cart"

                    # 检查是否有购买行为（模拟10%的购买率）
                    if recommendation_id % 10 == 0:
                        recommendation["purchased_at"] = recommendation["added_to_cart_at"] + timedelta(hours=3)
                        recommendation["status"] = "purchase"

            recommendation_data.append(recommendation)
            recommendation_id += 1

        # 根据门店和分类过滤
        filtered_data = []
        for rec in recommendation_data:
            if store_id and rec["store_id"] != store_id:
                continue
            if category_id and rec["category_id"] != category_id:
                continue
            filtered_data.append(rec)

        return filtered_data

    @staticmethod
    def _calculate_metrics(recommendation_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        计算推荐转化指标

        Args:
            recommendation_data: 推荐数据列表

        Returns:
            Dict: 转化指标
        """
        impressions = len(recommendation_data)
        clicks = sum(1 for rec in recommendation_data if rec["clicked_at"])
        add_to_carts = sum(1 for rec in recommendation_data if rec["added_to_cart_at"])
        purchases = sum(1 for rec in recommendation_data if rec["purchased_at"])

        # 计算比率
        click_rate = (clicks / impressions * 100) if impressions > 0 else 0
        cart_rate = (add_to_carts / clicks * 100) if clicks > 0 else 0
        purchase_rate = (purchases / add_to_carts * 100) if add_to_carts > 0 else 0
        conversion_rate = (purchases / impressions * 100) if impressions > 0 else 0

        return {
            "impressions": impressions,
            "clicks": clicks,
            "add_to_carts": add_to_carts,
            "purchases": purchases,
            "click_rate": round(click_rate, 2),
            "cart_rate": round(cart_rate, 2),
            "purchase_rate": round(purchase_rate, 2),
            "conversion_rate": round(conversion_rate, 2)
        }

    @staticmethod
    def _generate_trends(recommendation_data: List[Dict[str, Any]], start_date: date, end_date: date, granularity: str) -> List[Dict[str, Any]]:
        """
        生成趋势数据

        Args:
            recommendation_data: 推荐数据列表
            start_date: 开始日期
            end_date: 结束日期
            granularity: 时间粒度

        Returns:
            List[Dict]: 趋势数据列表
        """
        trends = []
        current_date = start_date

        while current_date <= end_date:
            # 根据粒度确定日期范围
            if granularity == "day":
                period_start = current_date
                period_end = current_date
                period_key = current_date.isoformat()
            elif granularity == "week":
                period_start = current_date
                period_end = current_date + timedelta(days=6)
                period_key = f"{current_date.isoformat()}~{period_end.isoformat()}"
            elif granularity == "month":
                period_start = current_date
                # 计算月末
                if current_date.month == 12:
                    period_end = date(current_date.year + 1, 1, 1) - timedelta(days=1)
                else:
                    period_end = date(current_date.year, current_date.month + 1, 1) - timedelta(days=1)
                period_key = f"{current_date.year}-{current_date.month:02d}"
            else:
                period_start = current_date
                period_end = current_date
                period_key = current_date.isoformat()

            # 过滤该时间段的数据
            period_data = [
                rec for rec in recommendation_data
                if rec["recommended_at"].date() >= period_start and rec["recommended_at"].date() <= period_end
            ]

            # 计算该时间段的指标
            metrics = ReportsService._calculate_metrics(period_data)

            trends.append({
                "date": period_key,
                "metrics": metrics
            })

            # 移动到下一个时间段
            if granularity == "day":
                current_date += timedelta(days=1)
            elif granularity == "week":
                current_date += timedelta(days=7)
            elif granularity == "month":
                if current_date.month == 12:
                    current_date = date(current_date.year + 1, 1, 1)
                else:
                    current_date = date(current_date.year, current_date.month + 1, 1)
            else:
                current_date += timedelta(days=1)

        return trends

    @staticmethod
    def _generate_details(recommendation_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        生成详细数据

        Args:
            recommendation_data: 推荐数据列表

        Returns:
            List[Dict]: 详细数据列表
        """
        return recommendation_data