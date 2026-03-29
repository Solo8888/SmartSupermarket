# Sales Trend Service
# Implements logic for sales trend analysis

from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy import func, and_, extract
from sqlalchemy.orm import Session
from models import Order, OrderItem, Product, Category
from core.logger import logger
from .schemas import SalesTrendData


class SalesTrendService:
    """销售趋势服务类"""
    
    def __init__(self):
        from models import get_db
        self.get_db = get_db
    
    def get_sales_trend(
        self, 
        start_date: Optional[str] = None, 
        end_date: Optional[str] = None, 
        store_id: Optional[str] = None, 
        category_id: Optional[str] = None, 
        period: str = "daily"
    ) -> List[SalesTrendData]:
        """获取销售趋势数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)，默认最近30天
            end_date: 结束日期 (YYYY-MM-DD)，默认今天
            store_id: 门店ID（可选）
            category_id: 商品分类ID（可选）
            period: 时间周期 (daily/weekly/monthly)
            
        Returns:
            销售趋势数据列表
        """
        db = next(self.get_db())
        
        try:
            # 处理日期参数
            if not end_date:
                end_date = datetime.now().strftime("%Y-%m-%d")
            
            if not start_date:
                # 默认最近30天
                end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
                start_date_obj = end_date_obj - timedelta(days=30)
                start_date = start_date_obj.strftime("%Y-%m-%d")
            
            # 构建查询
            query = db.query(
                Order.created_at,
                Order.final_amount,
                OrderItem.product_id,
                Product.category_id
            ).join(
                OrderItem, Order.id == OrderItem.order_id
            ).outerjoin(
                Product, OrderItem.product_id == Product.id
            ).filter(
                Order.status.in_(["paid", "shipped", "delivered", "completed"]),
                Order.created_at >= start_date,
                Order.created_at <= end_date + " 23:59:59"
            )
            
            # 应用过滤条件
            if store_id:
                # 假设订单表中有store_id字段
                query = query.filter(Order.store_id == store_id)
            
            if category_id:
                query = query.filter(Product.category_id == category_id)
            
            # 执行查询
            results = query.all()
            
            # 按时间周期分组
            grouped_data = self._group_by_period(results, period)
            
            # 转换为响应模型
            return [
                SalesTrendData(
                    period=period_key,
                    total_sales=sum(item["sales"] for item in items),
                    order_count=len(items),
                    average_order_value=sum(item["sales"] for item in items) / len(items) if items else 0
                )
                for period_key, items in sorted(grouped_data.items())
            ]
        
        except Exception as e:
            logger.error(f"获取销售趋势数据失败: {str(e)}")
            raise
        finally:
            db.close()
    
    def _group_by_period(self, results: List, period: str) -> Dict[str, List[Dict[str, Any]]]:
        """按时间周期分组数据
        
        Args:
            results: 查询结果列表
            period: 时间周期 (daily/weekly/monthly)
            
        Returns:
            按时间周期分组的数据
        """
        grouped = {}
        
        for result in results:
            created_at = result[0]
            sales = result[1]
            
            if period == "daily":
                # 按日期分组 (YYYY-MM-DD)
                period_key = created_at.strftime("%Y-%m-%d")
            elif period == "weekly":
                # 按周分组 (YYYY-Www)
                year, week, _ = created_at.isocalendar()
                period_key = f"{year}-W{week:02d}"
            elif period == "monthly":
                # 按月分组 (YYYY-MM)
                period_key = created_at.strftime("%Y-%m")
            else:
                period_key = created_at.strftime("%Y-%m-%d")
            
            if period_key not in grouped:
                grouped[period_key] = []
            
            grouped[period_key].append({"sales": sales})
        
        return grouped
