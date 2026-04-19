from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType
import os

# Initialize Spark Session for Streaming Simulation
spark = SparkSession.builder \
    .appName("OmniRetailStreaming") \
    .config("spark.sql.streaming.checkpointLocation", "data/raw/streaming_checkpoints") \
    .getOrCreate()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
STREAM_LANDING_DIR = os.path.join(BASE_DIR, 'data', 'raw', 'streaming_landing')
STAGING_DIR = os.path.join(BASE_DIR, 'data', 'staging')

# Target Schema for Sales Transactions
sales_schema = StructType([
    StructField("transaction_id", StringType(), False),
    StructField("date", TimestampType(), True),
    StructField("customer_id", StringType(), True),
    StructField("product_id", StringType(), True),
    StructField("store_id", StringType(), True),
    StructField("promotion_id", StringType(), True),
    StructField("units_sold", IntegerType(), True),
    StructField("total_amount", DoubleType(), True),
    StructField("discounted_amount", DoubleType(), True)
])

def run_streaming_ingestion():
    print(f"Monitoring landing zone: {STREAM_LANDING_DIR}")
    
    # 1. Initialize Source Stream
    raw_stream = spark.readStream \
        .option("header", "true") \
        .schema(sales_schema) \
        .csv(STREAM_LANDING_DIR)
    
    # 2. Add technical metadata
    processed_stream = raw_stream.withColumn("ingested_at", current_timestamp()) \
                                  .withColumn("ingestion_mode", lit("Streaming"))
    
    # 3. Sink Stream to Parquet
    query = processed_stream.writeStream \
        .format("parquet") \
        .option("path", os.path.join(STAGING_DIR, "streaming_sales.parquet")) \
        .option("checkpointLocation", os.path.join(BASE_DIR, "data", "raw", "streaming_checkpoints")) \
        .outputMode("append") \
        .start()

    print("Stream active. Listening for new files...")
    query.awaitTermination()

if __name__ == "__main__":
    if not os.path.exists(STREAM_LANDING_DIR):
        os.makedirs(STREAM_LANDING_DIR)
        
    try:
        run_streaming_ingestion()
    except KeyboardInterrupt:
        print("Streaming halted by user.")
    except Exception as e:
        print(f"Streaming Error: {e}")
    finally:
        spark.stop()
