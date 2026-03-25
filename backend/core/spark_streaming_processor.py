from pyspark.sql import SparkSession
from pyspark.sql.functions import col, window, sum, avg, count
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, FloatType, TimestampType
import os

# Kafka配置
KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092'
KAFKA_TOPIC = 'customer_flow'

# MySQL配置
MYSQL_URL = 'jdbc:mysql://mysql:3306/smart_supermarket'
MYSQL_USER = os.getenv('MYSQL_USER', 'root')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'password')

# 定义数据结构
schema = StructType([
    StructField('store_id', StringType()),
    StructField('store_name', StringType()),
    StructField('category_id', StringType()),
    StructField('category_name', StringType()),
    StructField('date', StringType()),
    StructField('weekday', IntegerType()),
    StructField('hour', IntegerType()),
    StructField('foot_traffic', IntegerType()),
    StructField('sales_amount', FloatType()),
    StructField('is_weekend', IntegerType()),
    StructField('timestamp', TimestampType())
])

class SparkStreamingProcessor:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("CustomerFlowProcessor") \
            .config("spark.sql.shuffle.partitions", "3") \
            .getOrCreate()
    
    def process_stream(self):
        """处理Kafka流数据"""
        # 从Kafka读取数据
        df = self.spark.readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP_SERVERS) \
            .option("subscribe", KAFKA_TOPIC) \
            .option("startingOffsets", "latest") \
            .load()
        
        # 解析JSON数据
        from pyspark.sql.functions import from_json
        df = df.selectExpr("CAST(value AS STRING)") \
            .select(from_json(col("value"), schema).alias("data")) \
            .select("data.*")
        
        # 5分钟窗口聚合
        windowed_df = df \
            .groupBy(
                window(col("timestamp"), "5 minutes"),
                col("store_id"),
                col("category_id")
            ) \
            .agg(
                sum("foot_traffic").alias("total_flow"),
                sum("sales_amount").alias("total_sales"),
                avg("foot_traffic").alias("avg_flow"),
                count("*").alias("event_count")
            )
        
        # 写入MySQL
        def write_to_mysql(batch_df, batch_id):
            batch_df.write \
                .format("jdbc") \
                .option("url", MYSQL_URL) \
                .option("dbtable", "customer_flow_realtime") \
                .option("user", MYSQL_USER) \
                .option("password", MYSQL_PASSWORD) \
                .mode("append") \
                .save()
        
        # 启动流处理
        query = windowed_df.writeStream \
            .foreachBatch(write_to_mysql) \
            .outputMode("update") \
            .start()
        
        query.awaitTermination()
    
    def run(self):
        """运行处理器"""
        try:
            self.process_stream()
        finally:
            self.spark.stop()

if __name__ == "__main__":
    processor = SparkStreamingProcessor()
    processor.run()
