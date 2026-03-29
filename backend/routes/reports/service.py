# Reports service
# Implement business logic for reports

import os
import json
import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, extract
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional
from .schemas import RecommendationConversionRequest, RecommendationConversionResponse, RecommendationConversionMetrics, RecommendationConversionTrend, RecommendationConversionDetail, ExportRequest, ExportResponse
from models.product import Product
from models.order import Order, OrderItem
from models.cart import Cart, CartItem

# 简单的内存缓存
_cache = {}
_CACHE_TTL = 3600  # 缓存过期时间（秒）

# 导出文件存储目录
EXPORT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'uploads', 'exports')
os.makedirs(EXPORT_DIR, exist_ok=True)


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

    @staticmethod
    def export_report(db: Session, request: ExportRequest) -> Dict[str, Any]:
        """
        导出报表

        Args:
            db: 数据库会话
            request: 导出请求参数

        Returns:
            Dict: 导出结果
        """
        # 根据报表类型获取数据
        if request.report_type == 'recommendation_conversion':
            # 构建推荐转化率分析请求
            conversion_request = RecommendationConversionRequest(
                start_date=request.start_date,
                end_date=request.end_date,
                store_id=request.store_id,
                category_id=request.category_id,
                time_granularity='day',
                include_details=True
            )
            
            # 获取分析数据
            data = ReportsService.get_recommendation_conversion(db, conversion_request)
        else:
            raise ValueError(f"不支持的报表类型: {request.report_type}")

        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"{request.report_type}_{timestamp}"

        # 根据格式导出
        if request.format == 'json':
            file_path = ReportsService._export_to_json(data, file_name)
        elif request.format == 'csv':
            file_path = ReportsService._export_to_csv(data, file_name)
        elif request.format == 'excel':
            file_path = ReportsService._export_to_excel(data, file_name)
        else:
            raise ValueError(f"不支持的导出格式: {request.format}")

        # 生成文件URL
        file_url = f"/uploads/exports/{os.path.basename(file_path)}"
        file_size = os.path.getsize(file_path)

        return {
            "file_url": file_url,
            "file_name": os.path.basename(file_path),
            "format": request.format,
            "size": file_size
        }

    @staticmethod
    def _export_to_json(data: Dict[str, Any], file_name: str) -> str:
        """
        导出为JSON格式

        Args:
            data: 要导出的数据
            file_name: 文件名

        Returns:
            str: 文件路径
        """
        file_path = os.path.join(EXPORT_DIR, f"{file_name}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        return file_path

    @staticmethod
    def _export_to_csv(data: Dict[str, Any], file_name: str) -> str:
        """
        导出为CSV格式

        Args:
            data: 要导出的数据
            file_name: 文件名

        Returns:
            str: 文件路径
        """
        file_path = os.path.join(EXPORT_DIR, f"{file_name}.csv")
        
        # 准备数据
        rows = []
        
        # 添加汇总数据
        summary = data.get('summary', {})
        rows.append({
            '类型': '汇总',
            '展示次数': summary.get('impressions', 0),
            '点击次数': summary.get('clicks', 0),
            '加购次数': summary.get('add_to_carts', 0),
            '购买次数': summary.get('purchases', 0),
            '点击率(%)': summary.get('click_rate', 0),
            '加购率(%)': summary.get('cart_rate', 0),
            '购买率(%)': summary.get('purchase_rate', 0),
            '转化率(%)': summary.get('conversion_rate', 0),
            '日期': '',
            '商品ID': '',
            '商品名称': '',
            '门店ID': '',
            '分类ID': '',
            '用户ID': ''
        })
        
        # 添加趋势数据
        for trend in data.get('trends', []):
            rows.append({
                '类型': '趋势',
                '展示次数': trend['metrics'].get('impressions', 0),
                '点击次数': trend['metrics'].get('clicks', 0),
                '加购次数': trend['metrics'].get('add_to_carts', 0),
                '购买次数': trend['metrics'].get('purchases', 0),
                '点击率(%)': trend['metrics'].get('click_rate', 0),
                '加购率(%)': trend['metrics'].get('cart_rate', 0),
                '购买率(%)': trend['metrics'].get('purchase_rate', 0),
                '转化率(%)': trend['metrics'].get('conversion_rate', 0),
                '日期': trend.get('date', ''),
                '商品ID': '',
                '商品名称': '',
                '门店ID': '',
                '分类ID': '',
                '用户ID': ''
            })
        
        # 添加详细数据
        for detail in data.get('details', []):
            rows.append({
                '类型': '详细',
                '展示次数': 1,
                '点击次数': 1 if detail.get('clicked_at') else 0,
                '加购次数': 1 if detail.get('added_to_cart_at') else 0,
                '购买次数': 1 if detail.get('purchased_at') else 0,
                '点击率(%)': '',
                '加购率(%)': '',
                '购买率(%)': '',
                '转化率(%)': '',
                '日期': detail.get('recommended_at', ''),
                '商品ID': detail.get('product_id', ''),
                '商品名称': detail.get('product_name', ''),
                '门店ID': detail.get('store_id', ''),
                '分类ID': detail.get('category_id', ''),
                '用户ID': detail.get('user_id', '')
            })
        
        # 创建DataFrame并导出
        df = pd.DataFrame(rows)
        df.to_csv(file_path, index=False, encoding='utf-8-sig')
        return file_path

    @staticmethod
    def _export_to_excel(data: Dict[str, Any], file_name: str) -> str:
        """
        导出为Excel格式

        Args:
            data: 要导出的数据
            file_name: 文件名

        Returns:
            str: 文件路径
        """
        file_path = os.path.join(EXPORT_DIR, f"{file_name}.xlsx")
        
        # 准备数据
        rows = []
        
        # 添加汇总数据
        summary = data.get('summary', {})
        rows.append({
            '类型': '汇总',
            '展示次数': summary.get('impressions', 0),
            '点击次数': summary.get('clicks', 0),
            '加购次数': summary.get('add_to_carts', 0),
            '购买次数': summary.get('purchases', 0),
            '点击率(%)': summary.get('click_rate', 0),
            '加购率(%)': summary.get('cart_rate', 0),
            '购买率(%)': summary.get('purchase_rate', 0),
            '转化率(%)': summary.get('conversion_rate', 0),
            '日期': '',
            '商品ID': '',
            '商品名称': '',
            '门店ID': '',
            '分类ID': '',
            '用户ID': ''
        })
        
        # 添加趋势数据
        for trend in data.get('trends', []):
            rows.append({
                '类型': '趋势',
                '展示次数': trend['metrics'].get('impressions', 0),
                '点击次数': trend['metrics'].get('clicks', 0),
                '加购次数': trend['metrics'].get('add_to_carts', 0),
                '购买次数': trend['metrics'].get('purchases', 0),
                '点击率(%)': trend['metrics'].get('click_rate', 0),
                '加购率(%)': trend['metrics'].get('cart_rate', 0),
                '购买率(%)': trend['metrics'].get('purchase_rate', 0),
                '转化率(%)': trend['metrics'].get('conversion_rate', 0),
                '日期': trend.get('date', ''),
                '商品ID': '',
                '商品名称': '',
                '门店ID': '',
                '分类ID': '',
                '用户ID': ''
            })
        
        # 添加详细数据
        for detail in data.get('details', []):
            rows.append({
                '类型': '详细',
                '展示次数': 1,
                '点击次数': 1 if detail.get('clicked_at') else 0,
                '加购次数': 1 if detail.get('added_to_cart_at') else 0,
                '购买次数': 1 if detail.get('purchased_at') else 0,
                '点击率(%)': '',
                '加购率(%)': '',
                '购买率(%)': '',
                '转化率(%)': '',
                '日期': detail.get('recommended_at', ''),
                '商品ID': detail.get('product_id', ''),
                '商品名称': detail.get('product_name', ''),
                '门店ID': detail.get('store_id', ''),
                '分类ID': detail.get('category_id', ''),
                '用户ID': detail.get('user_id', '')
            })
        
        # 创建DataFrame并导出
        df = pd.DataFrame(rows)
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='数据')
        return file_path