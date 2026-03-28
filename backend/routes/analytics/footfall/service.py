# Time distribution service
# Implements logic for time-based footfall distribution analysis

import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from .schemas import HourlyFootfall

from core.hdfs_client import hdfs_client


class TimeDistributionService:
    """时间分布服务类"""
    
    def get_time_distribution(self, start_date: str, end_date: str, store_id: Optional[str] = None) -> List[HourlyFootfall]:
        """获取时间分布数据
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            store_id: 门店ID（可选）
            
        Returns:
            按小时统计的客流分布数据
        """
        # 初始化小时计数器（00:00 - 23:00）
        hourly_counts = {f"{hour:02d}:00": 0 for hour in range(24)}
        
        print(f"Starting to get time distribution from {start_date} to {end_date} for store {store_id}")
        
        # 解析日期
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError as e:
            print(f"Invalid date format: {e}")
            return []
        
        # 遍历日期范围
        current_date = start
        while current_date <= end:
            # 遍历一天中的每个小时
            for hour in range(24):
                # 构建HDFS路径
                date_str = current_date.strftime("%Y-%m-%d")
                hour_str = f"{hour:02d}"
                hdfs_path = f"/customer_flow/{date_str}/{hour_str}/data.json"
                
                print(f"Checking HDFS path: {hdfs_path}")
                
                # 检查文件是否存在
                if self._file_exists(hdfs_path):
                    print(f"File exists: {hdfs_path}")
                    # 读取文件内容
                    file_content = self._read_hdfs_file(hdfs_path)
                    if file_content:
                        print(f"File content length: {len(file_content)}")
                        # 解析JSON数据
                        try:
                            data = json.loads(file_content)
                            print(f"Parsed data: {data}")
                            
                            # 过滤门店ID（如果指定）
                            if store_id is not None and store_id != "":
                                print(f"Filtering by store_id: {store_id}")
                                data = [item for item in data if item.get("store_id") == store_id]
                                print(f"Filtered data: {data}")
                            
                            # 统计客流量
                            for item in data:
                                customer_count = item.get("customer_count", 0)
                                hourly_key = f"{hour:02d}:00"
                                hourly_counts[hourly_key] += customer_count
                        except json.JSONDecodeError as e:
                            print(f"Error parsing JSON: {e}")
                    else:
                        print(f"Failed to read file content for {hdfs_path}")
                else:
                    print(f"File does not exist: {hdfs_path}")
            
            # 移动到下一天
            current_date += timedelta(days=1)
        
        # 转换为响应模型
        result = []
        for hour, count in hourly_counts.items():
            result.append(HourlyFootfall(hour=hour, count=count))
        
        print(f"Final time distribution result: {result}")
        return result
    
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
                print(f"Attempting to read file: {hdfs_path}")
                content = hdfs_client.read_file(hdfs_path)
                print(f"Read file result: {content}")
                return content
            except Exception as e:
                print(f"Error reading HDFS file (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    print("Retrying...")
                    time.sleep(2)
                else:
                    print("All retry attempts failed")
                    return None


class ExportService:
    """导出服务类"""
    
    def get_footfall_data(self, start_date: str, end_date: str, store_id: Optional[str] = None) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        """获取客流数据用于导出
        
        Args:
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            store_id: 门店ID（可选）
            
        Returns:
            元组：(原始客流数据列表, 按小时统计的客流量)
        """
        raw_data = []
        hourly_counts = {f"{hour:02d}:00": 0 for hour in range(24)}
        
        print(f"Starting to get footfall data for export from {start_date} to {end_date} for store {store_id}")
        
        # 解析日期
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError as e:
            print(f"Invalid date format: {e}")
            return [], hourly_counts
        
        # 遍历日期范围
        current_date = start
        while current_date <= end:
            # 遍历一天中的每个小时
            for hour in range(24):
                # 构建HDFS路径
                date_str = current_date.strftime("%Y-%m-%d")
                hour_str = f"{hour:02d}"
                hdfs_path = f"/customer_flow/{date_str}/{hour_str}/data.json"
                
                print(f"Checking HDFS path: {hdfs_path}")
                
                # 检查文件是否存在
                if self._file_exists(hdfs_path):
                    print(f"File exists: {hdfs_path}")
                    # 读取文件内容
                    file_content = self._read_hdfs_file(hdfs_path)
                    if file_content:
                        print(f"File content length: {len(file_content)}")
                        # 解析JSON数据
                        try:
                            data = json.loads(file_content)
                            print(f"Parsed data: {data}")
                            
                            # 过滤门店ID（如果指定）
                            if store_id is not None and store_id != "":
                                print(f"Filtering by store_id: {store_id}")
                                data = [item for item in data if item.get("store_id") == store_id]
                                print(f"Filtered data: {data}")
                            
                            # 收集原始数据
                            for item in data:
                                # 添加日期和小时信息
                                item["date"] = date_str
                                item["hour"] = hour
                                raw_data.append(item)
                                
                                # 统计客流量
                                customer_count = item.get("customer_count", 0)
                                hourly_key = f"{hour:02d}:00"
                                hourly_counts[hourly_key] += customer_count
                        except json.JSONDecodeError as e:
                            print(f"Error parsing JSON: {e}")
                    else:
                        print(f"Failed to read file content for {hdfs_path}")
                else:
                    print(f"File does not exist: {hdfs_path}")
            
            # 移动到下一天
            current_date += timedelta(days=1)
        
        print(f"Final raw data count: {len(raw_data)}")
        print(f"Final hourly counts: {hourly_counts}")
        return raw_data, hourly_counts
    
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
                print(f"Attempting to read file: {hdfs_path}")
                content = hdfs_client.read_file(hdfs_path)
                print(f"Read file result: {content}")
                return content
            except Exception as e:
                print(f"Error reading HDFS file (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    print("Retrying...")
                    time.sleep(2)
                else:
                    print("All retry attempts failed")
                    return None