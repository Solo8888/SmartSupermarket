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

def init_tables():
    """初始化客流数据相关表"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # 创建摄像头表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS cameras (
            id INT AUTO_INCREMENT PRIMARY KEY,
            camera_id VARCHAR(36),
            store_id VARCHAR(36),
            category_id VARCHAR(36),
            name VARCHAR(100),
            location VARCHAR(255),
            status ENUM('active', 'inactive') DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
        """)
        
        # 创建实时客流表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_flow_realtime (
            id INT AUTO_INCREMENT PRIMARY KEY,
            window_start DATETIME,
            window_end DATETIME,
            store_id VARCHAR(36),
            category_id VARCHAR(36),
            camera_id VARCHAR(36),
            total_flow INT,
            total_sales DECIMAL(10,2),
            avg_flow DECIMAL(10,2),
            event_count INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 创建小时客流统计表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_flow_hourly (
            id INT AUTO_INCREMENT PRIMARY KEY,
            store_id VARCHAR(36),
            category_id VARCHAR(36),
            camera_id VARCHAR(36),
            date DATE,
            hour INT,
            foot_traffic INT,
            sales_amount DECIMAL(10,2),
            is_weekend TINYINT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_store_category_date_hour (store_id, category_id, date, hour)
        )
        """)
        
        # 创建区域热度表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS customer_flow_heatmap (
            id INT AUTO_INCREMENT PRIMARY KEY,
            store_id VARCHAR(36),
            category_id VARCHAR(36),
            category_name VARCHAR(50),
            date DATE,
            hour INT,
            heat_value DECIMAL(5,2),  -- 热度值，0-10
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_store_category_date_hour (store_id, category_id, date, hour)
        )
        """)
        
        conn.commit()
        print("Tables initialized successfully")
        conn.close()
    except Exception as e:
        print(f"Error initializing tables: {e}")

if __name__ == "__main__":
    init_tables()
