from pyspark.sql import SparkSession
from pyspark.sql.functions import current_timestamp, lit
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType, TimestampType
import os
import sys

# Initialize Spark
spark = SparkSession.builder \
    .appName("OmniRetailIngestion") \
    .config("spark.sql.parquet.compression.codec", "snappy") \
    .getOrCreate()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
STAGING_DIR = os.path.join(BASE_DIR, 'data', 'staging')

# Schema definitions for primary entities
file_map = {
    "brands": {
        "file": "raw_brands.csv",
        "schema": StructType([
            StructField("brand_id", StringType(), False),
            StructField("brand_name", StringType(), True),
            StructField("category", StringType(), True)
        ])
    },
    "customers": {
        "file": "raw_customers.csv",
        "schema": StructType([
            StructField("customer_id", StringType(), False),
            StructField("name", StringType(), True),
            StructField("gender", StringType(), True),
            StructField("age", IntegerType(), True),
            StructField("city", StringType(), True),
            StructField("region", StringType(), True)
        ])
    },
    "sales": {
        "file": "raw_sales.csv",
        "schema": StructType([
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
    }
}

def ingest_all():
    print("Beginning PySpark Batch Ingestion...")
    
    for tname, config in file_map.items():
        raw_path = os.path.join(RAW_DIR, config["file"])
        output_path = os.path.join(STAGING_DIR, f"{tname}.parquet")
        
        if not os.path.exists(raw_path):
            print(f"Skipping {tname}: File not found at {raw_path}")
            continue
            
        print(f"Processing {config['file']}...")
        
        # Read from raw CSV
        df = spark.read.csv(raw_path, header=True, schema=config["schema"])
        
        # Add technical metadata for auditability
        df_final = df.withColumn("ingestion_timestamp", current_timestamp()) \
                     .withColumn("source_filename", lit(config["file"]))
        
        # Overwrite output for idempotency
        df_final.write.mode("overwrite").parquet(output_path)
        
        print(f"Loaded {df_final.count()} records into {output_path}")

if __name__ == "__main__":
    try:
        if not os.path.exists(STAGING_DIR):
            os.makedirs(STAGING_DIR)
        ingest_all()
        print("PySpark Ingestion Process Complete.")
    except Exception as e:
        print(f"Ingestion Failure: {e}")
        sys.exit(1)
    finally:
        spark.stop()
