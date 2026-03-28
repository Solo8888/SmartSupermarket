# 客流数据生成器模块
# 实现每小时生成所有门店的客流数据，符合生鲜超市的一般规律

import os
import time
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

# 尝试相对导入，如果失败则使用绝对导入
try:
    from .hdfs_client import hdfs_client
except ImportError:
    from hdfs_client import hdfs_client


class CustomerFlowGenerator:
    """客流数据生成器类"""
    
    def __init__(self):
        """初始化客流数据生成器"""
        self.store_data = []  # 门店数据
        self.data_retention_years = 3  # 数据保留年数
    
    def generate_customer_flow(self, store_id: str, timestamp: datetime) -> Dict[str, Any]:
        """生成单个门店的客流数据
        
        Args:
            store_id: 门店ID
            timestamp: 时间戳
            
        Returns:
            客流数据字典
        """
        # 计算基础客流
        base_flow = 100
        
        # 根据星期几调整客流（周末客流更多）
        weekday = timestamp.weekday()
        if weekday in [5, 6]:  # 周六、周日
            base_flow *= 1.5
        
        # 根据时间调整客流（晚高峰）
        hour = timestamp.hour
        if 6 <= hour < 9:  # 早高峰
            base_flow *= 1.2
        elif 17 <= hour < 22:  # 晚高峰
            base_flow *= 1.8
        elif hour < 6 or hour >= 22:  # 非营业时间
            base_flow = 0
        
        # 添加随机波动
        flow = int(base_flow * (0.8 + random.random() * 0.4))
        
        # 构建客流数据
        data = {
            "store_id": store_id,
            "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "customer_count": flow,
            "hour": hour,
            "weekday": weekday
        }
        
        return data
    
    def get_stores(self) -> List[Dict[str, Any]]:
        """获取门店列表
        
        Returns:
            门店列表
        """
        # 模拟门店数据，避免依赖数据库
        return [
            {"id": "store1", "name": "Store 1"},
            {"id": "store2", "name": "Store 2"},
            {"id": "store3", "name": "Store 3"}
        ]
    
    def generate_for_all_stores(self, timestamp: datetime) -> List[Dict[str, Any]]:
        """为所有门店生成客流数据
        
        Args:
            timestamp: 时间戳
            
        Returns:
            所有门店的客流数据列表
        """
        stores = self.get_stores()
        all_data = []
        
        for store in stores:
            data = self.generate_customer_flow(store["id"], timestamp)
            all_data.append(data)
        
        return all_data
    
    def save_to_hdfs(self, data: List[Dict[str, Any]], timestamp: datetime):
        """将客流数据存储到HDFS
        
        Args:
            data: 客流数据列表
            timestamp: 时间戳
        """
        # 构建HDFS存储路径
        date_str = timestamp.strftime("%Y-%m-%d")
        hour_str = timestamp.strftime("%H")
        hdfs_path = f"/customer_flow/{date_str}/{hour_str}"
        hdfs_file_path = f"{hdfs_path}/data.json"
        
        # 构建本地临时文件路径
        temp_file = f"/tmp/customer_flow_{timestamp.strftime('%Y%m%d%H')}.json"
        
        # 写入本地临时文件
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            # 上传到HDFS
            retries = 3
            for attempt in range(retries):
                try:
                    # 使用WebHDFS客户端上传文件
                    # 创建目录
                    hdfs_client.create_dir(hdfs_path)
                    # 上传文件
                    with open(temp_file, 'rb') as f:
                        data_bytes = f.read()
                    if hdfs_client.write_file(hdfs_file_path, data_bytes):
                        print(f"Data saved to HDFS: {hdfs_file_path}")
                        break
                    else:
                        raise Exception("Failed to write file to HDFS")
                except Exception as e:
                    print(f"Error saving data to HDFS (attempt {attempt + 1}/{retries}): {e}")
                    if attempt < retries - 1:
                        print("Retrying...")
                        time.sleep(2)
                    else:
                        print("All retry attempts failed")
        except Exception as e:
            print(f"Error writing temporary file: {e}")
        finally:
            # 删除本地临时文件
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except Exception as e:
                    print(f"Error removing temporary file: {e}")
    
    def delete_old_data(self):
        """删除超过保留年限的数据"""
        # 计算保留期限
        retention_date = datetime.now() - timedelta(days=self.data_retention_years * 365)
        retention_date_str = retention_date.strftime("%Y-%m-%d")
        
        # 检查并删除早于保留日期的所有数据
        hdfs_base_path = "/customer_flow"
        
        # 列出所有日期目录
        date_dirs = hdfs_client.list_dir(hdfs_base_path)
        if not date_dirs:
            print("No data directories found")
            return
        
        for date_dir in date_dirs:
            if date_dir.get('type') != 'DIRECTORY':
                continue
            
            date_str = date_dir.get('pathSuffix')
            
            # 检查日期是否早于保留日期
            if date_str < retention_date_str:
                # 删除整个日期目录
                date_path = f"{hdfs_base_path}/{date_str}"
                if hdfs_client.delete(date_path, recursive=True):
                    print(f"Old data deleted: {date_path}")
                else:
                    print(f"Failed to delete: {date_path}")
    
    def check_data_exists(self, timestamp: datetime) -> bool:
        """检查指定时间的数据是否存在
        
        Args:
            timestamp: 时间戳
            
        Returns:
            数据是否存在
        """
        # 构建HDFS路径
        date_str = timestamp.strftime("%Y-%m-%d")
        hour_str = timestamp.strftime("%H")
        hdfs_path = f"/customer_flow/{date_str}/{hour_str}/data.json"
        
        # 检查文件是否存在
        retries = 3
        for attempt in range(retries):
            try:
                # 使用WebHDFS客户端检查文件
                return hdfs_client.exists(hdfs_path)
            except Exception as e:
                print(f"Error checking data existence (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    print("Retrying...")
                    time.sleep(2)
                else:
                    print("All retry attempts failed")
                    return False
    
    def complete_missing_data(self):
        """补全缺失的客流数据"""
        # 获取当前时间，调整到最近的整点
        now = datetime.now()
        current_hour = now.replace(minute=0, second=0, microsecond=0)
        
        # 检查最近24小时的数据
        for i in range(24):
            check_time = current_hour - timedelta(hours=i)
            
            # 检查数据是否存在
            if not self.check_data_exists(check_time):
                print(f"Missing data for {check_time}, generating...")
                
                # 生成缺失的数据
                data = self.generate_for_all_stores(check_time)
                
                # 存储到HDFS
                self.save_to_hdfs(data, check_time)
                print(f"Completed missing data for {check_time}")
    
    def run(self):
        """运行客流数据生成器"""
        # 获取当前时间，调整到最近的整点
        now = datetime.now()
        current_hour = now.replace(minute=0, second=0, microsecond=0)
        
        # 生成所有门店的客流数据
        data = self.generate_for_all_stores(current_hour)
        
        # 打印生成的数据
        print(f"Generated customer flow data for {current_hour}:")
        for item in data:
            print(json.dumps(item, ensure_ascii=False))
        
        # 存储到HDFS
        self.save_to_hdfs(data, current_hour)
        
        # 删除过期数据
        self.delete_old_data()
        
        # 补全缺失数据
        self.complete_missing_data()


if __name__ == "__main__":
    # 测试客流数据生成
    generator = CustomerFlowGenerator()
    generator.run()
