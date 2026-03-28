# 客流数据服务
# 实现客流数据的查询逻辑

import os
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from .schemas import CustomerFlowResponse

from ..core.hdfs_client import hdfs_client


class CustomerFlowService:
    """客流数据服务类"""
    
    def get_customer_flow_data(self, start_time: datetime, end_time: datetime, store_id: Optional[str] = None) -> List[CustomerFlowResponse]:
        """获取客流数据
        
        Args:
            start_time: 开始时间
            end_time: 结束时间
            store_id: 门店ID（可选）
            
        Returns:
            客流数据列表
        """
        data_list = []
        
        # 遍历时间范围，获取每个小时的数据
        current_time = start_time.replace(minute=0, second=0, microsecond=0)
        while current_time <= end_time:
            # 构建HDFS路径
            date_str = current_time.strftime("%Y-%m-%d")
            hour_str = current_time.strftime("%H")
            hdfs_path = f"/customer_flow/{date_str}/{hour_str}/data.json"
            
            # 检查文件是否存在
            if self._file_exists(hdfs_path):
                # 读取文件内容
                file_content = self._read_hdfs_file(hdfs_path)
                if file_content:
                    # 解析JSON数据
                    try:
                        data = json.loads(file_content)
                        
                        # 过滤门店ID（如果指定）
                        if store_id:
                            data = [item for item in data if item.get("store_id") == store_id]
                        
                        # 转换为响应模型
                        for item in data:
                            # 转换时间字符串为datetime对象
                            item["timestamp"] = datetime.strptime(item["timestamp"], "%Y-%m-%d %H:%M:%S")
                            data_list.append(CustomerFlowResponse(**item))
                    except json.JSONDecodeError as e:
                        print(f"Error parsing JSON: {e}")
            
            # 移动到下一个小时
            current_time += timedelta(hours=1)
        
        return data_list
    
    def _file_exists(self, hdfs_path: str) -> bool:
        """检查HDFS文件是否存在
        
        Args:
            hdfs_path: HDFS文件路径
            
        Returns:
            文件是否存在
        """
        retries = 3
        for attempt in range(retries):
            try:
                # 使用WebHDFS客户端检查文件
                return hdfs_client.exists(hdfs_path)
            except Exception as e:
                print(f"Error checking file existence (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    print("Retrying...")
                    time.sleep(2)
                else:
                    print("All retry attempts failed")
                    return False
    
    def _read_hdfs_file(self, hdfs_path: str) -> Optional[str]:
        """读取HDFS文件内容
        
        Args:
            hdfs_path: HDFS文件路径
            
        Returns:
            文件内容
        """
        retries = 3
        for attempt in range(retries):
            try:
                # 使用WebHDFS客户端读取文件
                return hdfs_client.read_file(hdfs_path)
            except Exception as e:
                print(f"Error reading HDFS file (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    print("Retrying...")
                    time.sleep(2)
                else:
                    print("All retry attempts failed")
                    return None