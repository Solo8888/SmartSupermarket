# Time distribution service
# Implements logic for time-based footfall distribution analysis

import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from .schemas import HourlyFootfall

from core.hdfs_client import hdfs_client


class HDFSHelper:
    """HDFS操作工具类
    
    提供统一的HDFS文件操作方法，避免代码重复
    """
    
    @staticmethod
    def file_exists(hdfs_path: str) -> bool:
        """检查HDFS文件是否存在
        
        Args:
            hdfs_path: HDFS文件路径
            
        Returns:
            文件是否存在
        """
        retries = 3
        for attempt in range(retries):
            try:
                return hdfs_client.exists(hdfs_path)
            except Exception as e:
                print(f"Error checking file existence (attempt {attempt + 1}/{retries}): {e}")
                if attempt < retries - 1:
                    print("Retrying...")
                    time.sleep(2)
                else:
                    print("All retry attempts failed")
                    return False
    
    @staticmethod
    def read_file(hdfs_path: str) -> Optional[str]:
        """读取HDFS文件内容
        
        Args:
            hdfs_path: HDFS文件路径
            
        Returns:
            文件内容，读取失败返回None
        """
        retries = 3
        for attempt in range(retries):
            try:
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
        hourly_counts = {f"{hour:02d}:00": 0 for hour in range(24)}
        
        print(f"Starting to get time distribution from {start_date} to {end_date} for store {store_id}")
        
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError as e:
            print(f"Invalid date format: {e}")
            return []
        
        current_date = start
        while current_date <= end:
            for hour in range(24):
                date_str = current_date.strftime("%Y-%m-%d")
                hour_str = f"{hour:02d}"
                hdfs_path = f"/customer_flow/{date_str}/{hour_str}/data.json"
                
                print(f"Checking HDFS path: {hdfs_path}")
                
                if HDFSHelper.file_exists(hdfs_path):
                    print(f"File exists: {hdfs_path}")
                    file_content = HDFSHelper.read_file(hdfs_path)
                    if file_content:
                        print(f"File content length: {len(file_content)}")
                        try:
                            data = json.loads(file_content)
                            print(f"Parsed data: {data}")
                            
                            if store_id is not None and store_id != "":
                                print(f"Filtering by store_id: {store_id}")
                                data = [item for item in data if item.get("store_id") == store_id]
                                print(f"Filtered data: {data}")
                            
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
            
            current_date += timedelta(days=1)
        
        result = []
        for hour, count in hourly_counts.items():
            result.append(HourlyFootfall(hour=hour, count=count))
        
        print(f"Final time distribution result: {result}")
        return result


class ComparisonService:
    """对比分析服务类"""
    
    def _get_week_range(self, ref_date: datetime) -> tuple:
        weekday = ref_date.weekday()
        monday = ref_date - timedelta(days=weekday)
        sunday = monday + timedelta(days=6)
        return monday, sunday
    
    def get_week_comparison(self, store_id: Optional[str] = None) -> List[Dict[str, Any]]:
        today = datetime.now()
        
        this_week_monday, this_week_sunday = self._get_week_range(today)
        # Fix: 正确计算上周的日期范围
        last_week_monday = this_week_monday - timedelta(days=7)
        last_week_sunday = this_week_sunday - timedelta(days=7)
        
        print(f"Getting week comparison: this week {this_week_monday} to {this_week_sunday}, last week {last_week_monday} to {last_week_sunday}")
        
        this_week_hourly = {f"{hour:02d}:00": 0 for hour in range(24)}
        last_week_hourly = {f"{hour:02d}:00": 0 for hour in range(24)}
        
        current_date = this_week_monday
        while current_date <= this_week_sunday:
            for hour in range(24):
                date_str = current_date.strftime("%Y-%m-%d")
                hour_str = f"{hour:02d}"
                hdfs_path = f"/customer_flow/{date_str}/{hour_str}/data.json"
                
                if HDFSHelper.file_exists(hdfs_path):
                    file_content = HDFSHelper.read_file(hdfs_path)
                    if file_content:
                        try:
                            data = json.loads(file_content)
                            if store_id:
                                data = [item for item in data if item.get("store_id") == store_id]
                            
                            for item in data:
                                customer_count = item.get("customer_count", 0)
                                hourly_key = f"{hour:02d}:00"
                                this_week_hourly[hourly_key] += customer_count
                        except json.JSONDecodeError as e:
                            print(f"Error parsing JSON: {e}")
            
            current_date += timedelta(days=1)
        
        current_date = last_week_monday
        while current_date <= last_week_sunday:
            for hour in range(24):
                date_str = current_date.strftime("%Y-%m-%d")
                hour_str = f"{hour:02d}"
                hdfs_path = f"/customer_flow/{date_str}/{hour_str}/data.json"
                
                if HDFSHelper.file_exists(hdfs_path):
                    file_content = HDFSHelper.read_file(hdfs_path)
                    if file_content:
                        try:
                            data = json.loads(file_content)
                            if store_id:
                                data = [item for item in data if item.get("store_id") == store_id]
                            
                            for item in data:
                                customer_count = item.get("customer_count", 0)
                                hourly_key = f"{hour:02d}:00"
                                last_week_hourly[hourly_key] += customer_count
                        except json.JSONDecodeError as e:
                            print(f"Error parsing JSON: {e}")
            
            current_date += timedelta(days=1)
        
        result = []
        for hour in range(24):
            hourly_key = f"{hour:02d}:00"
            result.append({
                "hour": hourly_key,
                "this_week": this_week_hourly[hourly_key],
                "last_week": last_week_hourly[hourly_key]
            })
        
        print(f"Week comparison result: {result}")
        return result
    
    def get_weekend_weekday_comparison(self, store_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取工作日与周末每小时客流对比
        
        Args:
            store_id: 门店ID（可选）
            
        Returns:
            每小时工作日和周末客流对比数据
        """
        today = datetime.now()
        
        this_week_monday, this_week_sunday = self._get_week_range(today)
        # Fix: 正确计算上周的日期范围
        last_week_monday = this_week_monday - timedelta(days=7)
        last_week_sunday = this_week_sunday - timedelta(days=7)
        
        print(f"Getting weekend/weekday hourly comparison: this week {this_week_monday} to {this_week_sunday}, last week {last_week_monday} to {last_week_sunday}")
        
        this_week_weekday_hourly = {f"{hour:02d}:00": {"count": 0, "days": 0} for hour in range(24)}
        this_week_weekend_hourly = {f"{hour:02d}:00": {"count": 0, "days": 0} for hour in range(24)}
        
        last_week_weekday_hourly = {f"{hour:02d}:00": {"count": 0, "days": 0} for hour in range(24)}
        last_week_weekend_hourly = {f"{hour:02d}:00": {"count": 0, "days": 0} for hour in range(24)}
        
        current_date = this_week_monday
        while current_date <= this_week_sunday:
            weekday = current_date.weekday()
            is_weekend = weekday in [5, 6]
            
            for hour in range(24):
                date_str = current_date.strftime("%Y-%m-%d")
                hour_str = f"{hour:02d}"
                hdfs_path = f"/customer_flow/{date_str}/{hour_str}/data.json"
                hourly_key = f"{hour:02d}:00"
                
                if HDFSHelper.file_exists(hdfs_path):
                    file_content = HDFSHelper.read_file(hdfs_path)
                    if file_content:
                        try:
                            data = json.loads(file_content)
                            if store_id:
                                data = [item for item in data if item.get("store_id") == store_id]
                            
                            for item in data:
                                customer_count = item.get("customer_count", 0)
                                if is_weekend:
                                    this_week_weekend_hourly[hourly_key]["count"] += customer_count
                                    this_week_weekend_hourly[hourly_key]["days"] += 1
                                else:
                                    this_week_weekday_hourly[hourly_key]["count"] += customer_count
                                    this_week_weekday_hourly[hourly_key]["days"] += 1
                        except json.JSONDecodeError as e:
                            print(f"Error parsing JSON: {e}")
            
            current_date += timedelta(days=1)
        
        current_date = last_week_monday
        while current_date <= last_week_sunday:
            weekday = current_date.weekday()
            is_weekend = weekday in [5, 6]
            
            for hour in range(24):
                date_str = current_date.strftime("%Y-%m-%d")
                hour_str = f"{hour:02d}"
                hdfs_path = f"/customer_flow/{date_str}/{hour_str}/data.json"
                hourly_key = f"{hour:02d}:00"
                
                if HDFSHelper.file_exists(hdfs_path):
                    file_content = HDFSHelper.read_file(hdfs_path)
                    if file_content:
                        try:
                            data = json.loads(file_content)
                            if store_id:
                                data = [item for item in data if item.get("store_id") == store_id]
                            
                            for item in data:
                                customer_count = item.get("customer_count", 0)
                                if is_weekend:
                                    last_week_weekend_hourly[hourly_key]["count"] += customer_count
                                    last_week_weekend_hourly[hourly_key]["days"] += 1
                                else:
                                    last_week_weekday_hourly[hourly_key]["count"] += customer_count
                                    last_week_weekday_hourly[hourly_key]["days"] += 1
                        except json.JSONDecodeError as e:
                            print(f"Error parsing JSON: {e}")
            
            current_date += timedelta(days=1)
        
        result = []
        for hour in range(24):
            hourly_key = f"{hour:02d}:00"
            
            this_week_weekday_avg = (
                this_week_weekday_hourly[hourly_key]["count"] / this_week_weekday_hourly[hourly_key]["days"]
                if this_week_weekday_hourly[hourly_key]["days"] > 0 else 0
            )
            this_week_weekend_avg = (
                this_week_weekend_hourly[hourly_key]["count"] / this_week_weekend_hourly[hourly_key]["days"]
                if this_week_weekend_hourly[hourly_key]["days"] > 0 else 0
            )
            
            last_week_weekday_avg = (
                last_week_weekday_hourly[hourly_key]["count"] / last_week_weekday_hourly[hourly_key]["days"]
                if last_week_weekday_hourly[hourly_key]["days"] > 0 else 0
            )
            last_week_weekend_avg = (
                last_week_weekend_hourly[hourly_key]["count"] / last_week_weekend_hourly[hourly_key]["days"]
                if last_week_weekend_hourly[hourly_key]["days"] > 0 else 0
            )
            
            result.append({
                "hour": hourly_key,
                "this_week_weekday": round(this_week_weekday_avg, 1),
                "this_week_weekend": round(this_week_weekend_avg, 1),
                "last_week_weekday": round(last_week_weekday_avg, 1),
                "last_week_weekend": round(last_week_weekend_avg, 1)
            })
        
        print(f"Weekend/weekday hourly comparison result: {result}")
        return result


class ForecastService:
    """预测服务类"""
    
    def get_forecast_data(self, date: str, store_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取预测客流数据
        
        基于历史数据生成预测值，使用过去7天同一时段的平均值作为预测
        
        Args:
            date: 预测日期 (YYYY-MM-DD)
            store_id: 门店ID（可选）
            
        Returns:
            每小时预测客流数据
        """
        from datetime import datetime, timedelta
        import random
        
        target_date = datetime.strptime(date, "%Y-%m-%d")
        
        # 获取过去7天的数据用于预测
        hourly_forecast = {hour: {"count": 0, "days": 0} for hour in range(24)}
        
        for day_offset in range(1, 8):  # 过去7天
            past_date = target_date - timedelta(days=day_offset)
            date_str = past_date.strftime("%Y-%m-%d")
            
            for hour in range(24):
                hour_str = f"{hour:02d}"
                hdfs_path = f"/customer_flow/{date_str}/{hour_str}/data.json"
                
                if HDFSHelper.file_exists(hdfs_path):
                    file_content = HDFSHelper.read_file(hdfs_path)
                    if file_content:
                        try:
                            data = json.loads(file_content)
                            if store_id:
                                data = [item for item in data if item.get("store_id") == store_id]
                            
                            for item in data:
                                customer_count = item.get("customer_count", 0)
                                hourly_forecast[hour]["count"] += customer_count
                                hourly_forecast[hour]["days"] += 1
                        except json.JSONDecodeError as e:
                            print(f"Error parsing JSON: {e}")
        
        # 计算预测值（平均值 + 随机波动）
        result = []
        for hour in range(24):
            if hourly_forecast[hour]["days"] > 0:
                avg_count = hourly_forecast[hour]["count"] / hourly_forecast[hour]["days"]
                # 添加随机波动 (-10% 到 +10%)
                variation = random.uniform(-0.1, 0.1)
                forecast_count = int(avg_count * (1 + variation))
            else:
                # 如果没有历史数据，使用默认值
                forecast_count = random.randint(10, 50)
            
            result.append({
                "hour": hour,
                "forecast_count": max(0, forecast_count)
            })
        
        print(f"Forecast data for {date}: {result}")
        return result


class ExportService:
    """导出服务类"""
    
    def get_footfall_data(self, start_date: str, end_date: str, store_id: Optional[str] = None) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
        raw_data = []
        hourly_counts = {f"{hour:02d}:00": 0 for hour in range(24)}
        
        print(f"Starting to get footfall data for export from {start_date} to {end_date} for store {store_id}")
        
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError as e:
            print(f"Invalid date format: {e}")
            return [], hourly_counts
        
        current_date = start
        while current_date <= end:
            for hour in range(24):
                date_str = current_date.strftime("%Y-%m-%d")
                hour_str = f"{hour:02d}"
                hdfs_path = f"/customer_flow/{date_str}/{hour_str}/data.json"
                
                print(f"Checking HDFS path: {hdfs_path}")
                
                if HDFSHelper.file_exists(hdfs_path):
                    print(f"File exists: {hdfs_path}")
                    file_content = HDFSHelper.read_file(hdfs_path)
                    if file_content:
                        print(f"File content length: {len(file_content)}")
                        try:
                            data = json.loads(file_content)
                            print(f"Parsed data: {data}")
                            
                            if store_id is not None and store_id != "":
                                print(f"Filtering by store_id: {store_id}")
                                data = [item for item in data if item.get("store_id") == store_id]
                                print(f"Filtered data: {data}")
                            
                            for item in data:
                                item["date"] = date_str
                                item["hour"] = hour
                                raw_data.append(item)
                                
                                customer_count = item.get("customer_count", 0)
                                hourly_key = f"{hour:02d}:00"
                                hourly_counts[hourly_key] += customer_count
                        except json.JSONDecodeError as e:
                            print(f"Error parsing JSON: {e}")
                    else:
                        print(f"Failed to read file content for {hdfs_path}")
                else:
                    print(f"File does not exist: {hdfs_path}")
            
            current_date += timedelta(days=1)
        
        print(f"Final raw data count: {len(raw_data)}")
        print(f"Final hourly counts: {hourly_counts}")
        return raw_data, hourly_counts
