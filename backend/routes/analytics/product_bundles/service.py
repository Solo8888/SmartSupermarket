
from typing import List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models.order import Order, OrderItem
from .schemas import ProductBundle, ProductBundlesResponse
from ..association_rules.service import AprioriAlgorithm
import uuid


class ProductBundlesService:
    """商品组合服务类"""
    
    def get_order_transactions(self, db, start_date, end_date):
        """从数据库获取订单交易数据
        
        Args:
            db: 数据库会话
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            
        Returns:
            交易数据列表，每个交易是商品名称的列表
        """
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            end = end.replace(hour=23, minute=59, second=59, microsecond=999999)
        except ValueError:
            return []
        
        orders = db.query(Order).filter(
            and_(
                Order.created_at >= start,
                Order.created_at <= end,
                Order.status.in_(['paid', 'shipped', 'delivered', 'completed'])
            )
        ).all()
        
        transactions = []
        for order in orders:
            order_items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
            product_names = [item.product_name for item in order_items]
            if product_names:
                transactions.append(product_names)
        
        return transactions
    
    def get_product_bundles(self, db, start_date, end_date, 
                              min_support=0.01, min_confidence=0.5):
        """获取商品组合
        
        Args:
            db: 数据库会话
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            min_support: 最小支持度 (0-1)
            min_confidence: 最小置信度 (0-1)
            
        Returns:
            商品组合响应
        """
        transactions = self.get_order_transactions(db, start_date, end_date)
        
        if not transactions:
            return ProductBundlesResponse(bundles=[])
        
        apriori = AprioriAlgorithm(transactions, min_support, min_confidence)
        frequent_itemsets = apriori.find_frequent_itemsets()
        
        bundles = []
        for item_set in frequent_itemsets:
            if len(item_set) >= 2:
                item_list = list(item_set)
                item_list.sort()
                
                item_set_support = apriori.item_counts.get(item_set, 0)
                support = item_set_support / len(transactions) if len(transactions) > 0 else 0
                
                expected_sales_increase = support * min_confidence
                
                bundle = ProductBundle(
                    bundle_id=str(uuid.uuid4()),
                    products=item_list,
                    expected_sales_increase=expected_sales_increase
                )
                bundles.append(bundle)
        
        bundles.sort(key=lambda x: x.expected_sales_increase, reverse=True)
        
        return ProductBundlesResponse(bundles=bundles)
