from sqlalchemy.orm import Session
from datetime import date
from typing import List, Dict
import os
from dotenv import load_dotenv

from .schemas import CustomerFlowHourlyItem

# 加载环境变量
load_dotenv()


class CustomerFlowService:
    """客流分析服务"""

    @staticmethod
    def get_hourly_customer_flow(db: Session, store_id: str, start_date: date, end_date: date) -> List[CustomerFlowHourlyItem]:
        """
        获取各时段客流分布

        Args:
            db: 数据库会话
            store_id: 门店ID
            start_date: 开始日期
            end_date: 结束日期

        Returns:
            各时段客流分布列表
        """
        hourly_data = []
        try:
            # 模拟 Hive 查询，返回模拟数据
            # 实际部署时，这里应该连接 Hive 执行真实查询
            print(f"Mock query: Getting hourly customer flow for store {store_id} from {start_date} to {end_date}")
            
            # 生成模拟数据
            flow_by_hour = {hour: 0 for hour in range(24)}
            for hour in range(24):
                if 9 <= hour <= 12 or 17 <= hour <= 20:
                    # 高峰期客流较多
                    flow_count = 150 + (hour - 9) * 20 if hour <= 12 else 150 + (20 - hour) * 20
                else:
                    # 低峰期客流较少
                    flow_count = 50 + hour * 2 if hour < 9 else 50 + (23 - hour) * 2
                flow_by_hour[hour] = flow_count
            
            # 转换为响应格式
            for hour in range(24):
                hourly_data.append(CustomerFlowHourlyItem(hour=hour, flow_count=flow_by_hour[hour]))
        except Exception as e:
            print(f"Error querying customer flow data: {e}")
            # 如果出错，使用模拟数据
            for hour in range(24):
                if 9 <= hour <= 12 or 17 <= hour <= 20:
                    # 高峰期客流较多
                    flow_count = 150 + (hour - 9) * 20 if hour <= 12 else 150 + (20 - hour) * 20
                else:
                    # 低峰期客流较少
                    flow_count = 50 + hour * 2 if hour < 9 else 50 + (23 - hour) * 2
                hourly_data.append(CustomerFlowHourlyItem(hour=hour, flow_count=flow_count))
        
        return hourly_data
