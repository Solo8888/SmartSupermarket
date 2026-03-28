from typing import List, Dict, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
from models.order import Order, OrderItem
from .schemas import AssociationRule, AssociationRulesResponse
import uuid


class AprioriAlgorithm:
    """Apriori算法实现类"""
    
    def __init__(self, transactions, min_support, min_confidence):
        self.transactions = transactions
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.total_transactions = len(transactions)
        self.item_counts = {}
    
    def _get_single_item_sets(self):
        """获取所有单个商品的频繁项集"""
        item_count = {}
        for transaction in self.transactions:
            for item in transaction:
                if item not in item_count:
                    item_count[item] = 0
                item_count[item] += 1
        
        single_items = []
        for item, count in item_count.items():
            support = count / self.total_transactions
            if support >= self.min_support:
                item_set = frozenset([item])
                self.item_counts[item_set] = count
                single_items.append(item_set)
        
        return single_items
    
    def _generate_candidates(self, item_sets, k):
        """生成候选k项集"""
        candidates = []
        num_sets = len(item_sets)
        
        for i in range(num_sets):
            for j in range(i + 1, num_sets):
                set1 = item_sets[i]
                set2 = item_sets[j]
                union = set1.union(set2)
                
                if len(union) == k:
                    if union not in candidates:
                        candidates.append(union)
        
        return candidates
    
    def _prune_candidates(self, candidates, prev_item_sets):
        """剪枝候选集"""
        pruned = []
        for candidate in candidates:
            is_valid = True
            subsets = [frozenset(candidate - {item}) for item in candidate]
            for subset in subsets:
                if subset not in prev_item_sets:
                    is_valid = False
                    break
            if is_valid:
                pruned.append(candidate)
        return pruned
    
    def _count_support(self, candidates):
        """计算候选集的支持度并筛选频繁项集"""
        frequent_items = []
        for candidate in candidates:
            count = 0
            for transaction in self.transactions:
                if candidate.issubset(transaction):
                    count += 1
            support = count / self.total_transactions
            if support >= self.min_support:
                self.item_counts[candidate] = count
                frequent_items.append(candidate)
        return frequent_items
    
    def find_frequent_itemsets(self):
        """找出所有频繁项集"""
        all_frequent = []
        current_k = 1
        
        single_items = self._get_single_item_sets()
        if not single_items:
            return []
        
        all_frequent.extend(single_items)
        current_item_sets = single_items
        
        while True:
            current_k += 1
            candidates = self._generate_candidates(current_item_sets, current_k)
            if not candidates:
                break
            
            pruned = self._prune_candidates(candidates, current_item_sets)
            if not pruned:
                break
            
            frequent = self._count_support(pruned)
            if not frequent:
                break
            
            all_frequent.extend(frequent)
            current_item_sets = frequent
        
        return all_frequent
    
    def _generate_rules_from_itemset(self, item_set):
        """从一个频繁项集生成关联规则"""
        rules = []
        if len(item_set) < 2:
            return rules
        
        item_set_list = list(item_set)
        
        from itertools import combinations
        for k in range(1, len(item_set_list)):
            for antecedent_tuple in combinations(item_set_list, k):
                antecedent = list(antecedent_tuple)
                consequent = [item for item in item_set_list if item not in antecedent]
                
                antecedent_set = frozenset(antecedent)
                if antecedent_set not in self.item_counts:
                    continue
                
                antecedent_support = self.item_counts[antecedent_set]
                item_set_support = self.item_counts[item_set]
                confidence = item_set_support / antecedent_support
                
                if confidence >= self.min_confidence:
                    support = item_set_support / self.total_transactions
                    rules.append((antecedent, consequent, support, confidence))
        
        return rules
    
    def generate_association_rules(self, frequent_itemsets):
        """生成关联规则"""
        all_rules = []
        
        for item_set in frequent_itemsets:
            rules = self._generate_rules_from_itemset(item_set)
            for antecedent, consequent, support, confidence in rules:
                rule = AssociationRule(
                    rule_id=str(uuid.uuid4()),
                    antecedent=antecedent,
                    consequent=consequent,
                    support=support,
                    confidence=confidence
                )
                all_rules.append(rule)
        
        return all_rules


class AssociationRulesService:
    """关联规则服务类"""
    
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
    
    def get_association_rules(self, db, start_date, end_date, 
                               min_support=0.01, min_confidence=0.5):
        """获取商品关联规则
        
        Args:
            db: 数据库会话
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            min_support: 最小支持度 (0-1)
            min_confidence: 最小置信度 (0-1)
            
        Returns:
            关联规则响应
        """
        transactions = self.get_order_transactions(db, start_date, end_date)
        
        if not transactions:
            return AssociationRulesResponse(rules=[])
        
        apriori = AprioriAlgorithm(transactions, min_support, min_confidence)
        frequent_itemsets = apriori.find_frequent_itemsets()
        rules = apriori.generate_association_rules(frequent_itemsets)
        
        return AssociationRulesResponse(rules=rules)
