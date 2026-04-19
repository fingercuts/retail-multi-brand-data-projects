import duckdb
import pandas as pd
from sqlalchemy import create_engine
import os
import sys

# Connection details - Using environment variables with defaults for Docker compatibility
POSTGRES_USER = os.getenv("POSTGRES_USER", "retail_user")
POSTGRES_PASS = os.getenv("POSTGRES_PASSWORD", "retail_pass")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB", "retail_serving")

# Dynamically calculate the project root directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DUCKDB_PATH = os.path.join(BASE_DIR, 'data', 'multibrand_retail.duckdb')

def serve_data():
    print("--- Starting Reverse ETL: DuckDB -> PostgreSQL ---")
    
    if not os.path.exists(DUCKDB_PATH):
        print(f"Error: DuckDB not found at {DUCKDB_PATH}. Run dbt-build first.")
        return

    # 1. Connect to DuckDB
    con = duckdb.connect(DUCKDB_PATH, read_only=True)
    
    # 2. Connect to PostgreSQL via SQLAlchemy
    pg_uri = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASS}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    engine = create_engine(pg_uri)

    # Tables to serve (the final Marts)
    tables_to_serve = ["fct_sales", "dim_customers", "dim_products", "dim_stores"]

    for table in tables_to_serve:
        try:
            print(f"Syncing {table} to PostgreSQL...")
            
            # Extract from DuckDB
            df = con.execute(f"SELECT * FROM {table}").df()
            
            # Load into PostgreSQL (Overwrite to keep 'serving layer' fresh)
            df.to_sql(table, engine, if_exists='replace', index=False)
            
            print(f" -> {len(df)} rows synced successfully.")
        except Exception as e:
            print(f" -> Failed to sync {table}: {e}")

    con.close()
    print("--- Serving Layer Update Complete ---")

if __name__ == "__main__":
    try:
        serve_data()
    except Exception as e:
        print(f"Critical error during sync: {e}")
        sys.exit(1)
