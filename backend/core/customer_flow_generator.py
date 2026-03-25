import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import time
from kafka import KafkaProducer
import pymysql
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库连接配置
DB_CONFIG = {
    'host': 'mysql',
    'user': os.getenv('MYSQL_USER', 'root'),
    'password': os.getenv('MYSQL_PASSWORD', 'password'),
    'database': os.getenv('MYSQL_DATABASE', 'smart_supermarket'),
    'port': 3306
}

# Kafka配置
KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092'
KAFKA_TOPIC = 'customer_flow'

# 基础客流基准（按小时，未加扰动）
hour_base = {}
for h in range(24):
    if h in [7, 8]:          # 早市高峰
        hour_base[h] = 400
    elif h in [11, 12, 13]:  # 午间简餐
        hour_base[h] = 350
    elif h in [17, 18]:      # 下班高峰
        hour_base[h] = 500
    elif h in [19, 20]:      # 晚间折扣高峰
        hour_base[h] = 600
    else:
        hour_base[h] = 150

# 区域倍率（不同区域在不同时段的活跃度）
region_factor = {
    '蔬菜区':    {'base': 1.2,  'peak_hours': [7,8,17,18]},
    '肉禽区':    {'base': 1.1,  'peak_hours': [7,8,17,18]},
    '熟食区':    {'base': 1.5,  'peak_hours': [11,12,13,19,20]},
    '烘焙区':    {'base': 1.3,  'peak_hours': [8,9,19,20]},
    '海鲜区':    {'base': 1.0,  'peak_hours': [10,11,17,18]},
    '收银区':    {'base': 0.8,  'peak_hours': [7,8,12,13,18,19,20]},  # 跟随整体客流
    '非生鲜区':  {'base': 0.6,  'peak_hours': [10,11,14,15]}
}

# 周末倍率（周六日整体提升）
weekend_factor = 1.5

class CustomerFlowGenerator:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.stores = self.get_stores()
        self.categories = self.get_categories()
    
    def get_stores(self):
        """从数据库获取门店列表"""
        stores = []
        try:
            conn = pymysql.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM stores")
            for row in cursor.fetchall():
                stores.append({'id': row[0], 'name': row[1]})
            conn.close()
        except Exception as e:
            print(f"Error getting stores: {e}")
            # 如果数据库连接失败，使用模拟数据
            for i in range(1, 6):
                stores.append({'id': f'store_{i}', 'name': f'门店{i}'})
        return stores
    
    def get_categories(self):
        """从数据库获取一级分类"""
        categories = []
        try:
            conn = pymysql.connect(**DB_CONFIG)
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM categories WHERE parent_id IS NULL")
            for row in cursor.fetchall():
                categories.append({'id': row[0], 'name': row[1]})
            conn.close()
        except Exception as e:
            print(f"Error getting categories: {e}")
            # 如果数据库连接失败，使用默认区域
            default_regions = ['蔬菜区', '肉禽区', '熟食区', '烘焙区', '海鲜区', '收银区', '非生鲜区']
            for i, region in enumerate(default_regions):
                categories.append({'id': f'cat_{i}', 'name': region})
        return categories
    
    def generate_flow_data(self, start_date, num_days=1):
        """生成客流数据"""
        data = []
        for store in self.stores:
            for day in range(num_days):
                current_date = start_date + timedelta(days=day)
                weekday = current_date.weekday()  # 0=Mon, 6=Sun
                is_weekend = 1 if weekday >= 5 else 0  # 周六5，周日6
                # 获取当前小时
                current_hour = datetime.now().hour
                # 生成当前小时和未来2小时的数据，模拟实时数据
                for hour in range(current_hour, min(current_hour + 3, 24)):
                    for category in self.categories:
                        # 基础客流
                        base = hour_base[hour]
                        # 区域调节
                        region_name = category['name']
                        rf = region_factor.get(region_name, {'base': 1.0, 'peak_hours': []})
                        region_mult = rf['base']
                        if hour in rf['peak_hours']:
                            region_mult *= 1.3  # 该区域高峰期再放大
                        # 周末调节
                        if is_weekend:
                            region_mult *= weekend_factor
                        # 加随机波动（-20% ~ +20%）
                        noise = np.random.uniform(0.8, 1.2)
                        foot_traffic = int(base * region_mult * noise)
                        # 销售额模拟：假设客单价约 5-15 元（不同区域差异）
                        price_per_person = np.random.uniform(5, 15) if region_name != '收银区' else np.random.uniform(20, 50)
                        sales_amount = round(foot_traffic * price_per_person, 2)
                        
                        # 生成事件数据
                        event = {
                            'store_id': store['id'],
                            'store_name': store['name'],
                            'category_id': category['id'],
                            'category_name': category['name'],
                            'date': current_date.strftime('%Y-%m-%d'),
                            'weekday': weekday,
                            'hour': hour,
                            'foot_traffic': foot_traffic,
                            'sales_amount': sales_amount,
                            'is_weekend': is_weekend,
                            'timestamp': datetime.now().isoformat()
                        }
                        data.append(event)
        return data
    
    def send_to_kafka(self, events):
        """将事件发送到Kafka"""
        for event in events:
            try:
                self.producer.send(KAFKA_TOPIC, event)
                print(f"Sent event: {event}")
                time.sleep(0.1)  # 模拟实时数据
            except Exception as e:
                print(f"Error sending event: {e}")
    
    def run(self):
        """运行数据生成器"""
        # 生成当天的数据
        start_date = datetime.now().date()
        events = self.generate_flow_data(start_date, num_days=1)
        self.send_to_kafka(events)
        self.producer.close()

if __name__ == "__main__":
    generator = CustomerFlowGenerator()
    generator.run()
