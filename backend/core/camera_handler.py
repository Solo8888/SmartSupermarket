# import cv2
import numpy as np
import json
import time
from kafka import KafkaProducer
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Kafka配置
KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092'
KAFKA_TOPIC = 'customer_flow'

class CameraHandler:
    """摄像头处理器，用于从摄像头获取客流数据"""
    
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        self.cameras = []  # 摄像头列表
    
    def initialize_cameras(self):
        """初始化摄像头"""
        # 这里可以添加摄像头初始化逻辑
        # 例如：
        # for i in range(4):  # 假设有4个摄像头
        #     cap = cv2.VideoCapture(i)
        #     if cap.isOpened():
        #         self.cameras.append(cap)
        #         print(f"Camera {i} initialized")
        print("Cameras initialized")
    
    def process_frame(self, frame, camera_id, store_id, category_id, category_name):
        """处理摄像头帧，识别客流"""
        # 这里可以添加客流识别逻辑
        # 例如使用YOLO或其他目标检测模型
        
        # 模拟客流数据
        import random
        foot_traffic = random.randint(10, 50)
        sales_amount = round(foot_traffic * random.uniform(5, 15), 2)
        
        # 生成事件数据
        event = {
            'store_id': store_id,
            'store_name': f'Store {store_id}',
            'category_id': category_id,
            'category_name': category_name,
            'date': time.strftime('%Y-%m-%d'),
            'weekday': time.localtime().tm_wday,
            'hour': time.localtime().tm_hour,
            'foot_traffic': foot_traffic,
            'sales_amount': sales_amount,
            'is_weekend': 1 if time.localtime().tm_wday >= 5 else 0,
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'camera_id': camera_id
        }
        
        return event
    
    def run(self):
        """运行摄像头处理器"""
        self.initialize_cameras()
        
        # 模拟摄像头数据
        while True:
            try:
                # 模拟从摄像头获取数据
                # 实际项目中应该从真实摄像头获取帧
                for i in range(4):  # 假设有4个摄像头
                    # 模拟不同区域的摄像头
                    categories = [
                        {'id': 'cat_1', 'name': '蔬菜区'},
                        {'id': 'cat_2', 'name': '肉禽区'},
                        {'id': 'cat_3', 'name': '熟食区'},
                        {'id': 'cat_4', 'name': '收银区'}
                    ]
                    
                    category = categories[i % len(categories)]
                    event = self.process_frame(
                        None,  # 实际项目中应该传递真实的帧
                        f'camera_{i}',
                        'store_1',
                        category['id'],
                        category['name']
                    )
                    
                    # 发送到Kafka
                    self.producer.send(KAFKA_TOPIC, event)
                    print(f"Sent camera event: {event}")
                    time.sleep(0.5)
                
                # 每10秒处理一次
                time.sleep(10)
            except Exception as e:
                print(f"Error in camera handler: {e}")
                time.sleep(5)
    
    def close(self):
        """关闭摄像头"""
        for cap in self.cameras:
            cap.release()
        self.producer.close()

if __name__ == "__main__":
    camera_handler = CameraHandler()
    try:
        camera_handler.run()
    finally:
        camera_handler.close()
