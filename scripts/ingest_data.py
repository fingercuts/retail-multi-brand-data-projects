import duckdb
import os
import logging
import time
import json
import pandas as pd
from datetime import datetime
from scripts.contracts import CONTRACTS_MAP

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("ingestion_details.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def validate_chunk_worker(records_chunk, tname):
    # Retrieve contract class mapped to the table name
    contract_class = CONTRACTS_MAP.get(tname)
    val = []
    inval = []
    for rec in records_chunk:
        try:
            validated = contract_class(**rec)
            val.append(validated.model_dump())
        except Exception as e:
            rec["_contract_error"] = str(e)
            inval.append(rec)
    return val, inval

class RetailDataIngestor:
    def __init__(self):
        # Dynamically calculate the project root directory relative to this script
        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_dir = os.path.dirname(self.script_dir)
        
        # Use relative paths for portability
        self.data_dir = os.path.join(self.base_dir, 'data')
        self.duckdb_path = os.path.join(self.data_dir, 'multibrand_retail.duckdb')
        self.staging_dir = os.path.join(self.data_dir, 'staging')
        self.raw_dir = os.path.join(self.data_dir, 'raw')
        self.dlq_dir = os.path.join(self.data_dir, 'dlq')
        
        # Ensure directories exist
        os.makedirs(self.staging_dir, exist_ok=True)
        os.makedirs(self.dlq_dir, exist_ok=True)
        
        # Table mapping: {table_name: {raw_file, staging_file}}
        self.file_map = {
            "raw_brands": {"raw": "brands.csv", "staging": "brands.parquet"},
            "raw_customers": {"raw": "customers.csv", "staging": "customers.parquet"},
            "raw_inventory": {"raw": "final_inventory.csv", "staging": "inventory.parquet"},
            "raw_channels": {"raw": "online_channels.csv", "staging": "channels.parquet"},
            "raw_products": {"raw": "products.csv", "staging": "products.parquet"},
            "raw_promotions": {"raw": "promotions.csv", "staging": "promotions.parquet"},
            "raw_sales": {"raw": "sales_transactions_simulated.csv", "staging": "sales.parquet"},
            "raw_stores": {"raw": "stores_enhanced.csv", "staging": "stores.parquet"}
        }

    def _get_connection(self):
        return duckdb.connect(self.duckdb_path)

    def run_ingestion(self):
        start_time = time.time()
        logger.info("--- Starting Multi-Brand Retail Ingestion ---")
        
        con = self._get_connection()
        
        # Create metadata table if not exists
        con.execute("CREATE TABLE IF NOT EXISTS ingestion_metadata (ingestion_id TIMESTAMP, table_name VARCHAR, status VARCHAR, source VARCHAR, row_count INTEGER, duration_sec DOUBLE)")

        total_rows = 0
        
        for tname, files in self.file_map.items():
            stg_path = os.path.join(self.staging_dir, files["staging"])
            raw_path = os.path.join(self.raw_dir, files["raw"])
            
            ingestion_start = time.time()
            source_used = None
            
            try:
                if os.path.exists(stg_path):
                    logger.info(f"Loading {files['staging']} into {tname}...")
                    con.execute(f"CREATE OR REPLACE TABLE {tname} AS SELECT * FROM read_parquet(?)", [stg_path])
                    source_used = "Parquet (Staging)"
                elif os.path.exists(raw_path):
                    logger.info(f"Parquet missing. Loading {files['raw']} into {tname}...")
                    
                    contract_class = CONTRACTS_MAP.get(tname)
                    if contract_class:
                        logger.info(f"Validating {tname} against schema contracts...")
                        valid_records = []
                        invalid_records = []
                        
                        # Use Pandas to read in chunks to save RAM
                        chunk_size = 50000
                        import concurrent.futures
                        import multiprocessing
                            
                        # Reading and submitting chunks dynamically
                        df_iterator = pd.read_csv(raw_path, chunksize=chunk_size, low_memory=False)
                        
                        with concurrent.futures.ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:
                            futures = []
                            for chunk_df in df_iterator:
                                chunk_records = chunk_df.to_dict(orient="records")
                                futures.append(executor.submit(validate_chunk_worker, chunk_records, tname))
                                
                            for future in concurrent.futures.as_completed(futures):
                                val, inval = future.result()
                                valid_records.extend(val)
                                invalid_records.extend(inval)
                        
                        if invalid_records:
                            logger.warning(f"Found {len(invalid_records)} invalid records! Routing to DLQ.")
                            dlq_file = os.path.join(self.dlq_dir, f"{tname}_dlq_{int(time.time())}.json")
                            with open(dlq_file, 'w') as f:
                                json.dump(invalid_records, f, default=str, indent=2)
                        
                        df = pd.DataFrame(valid_records)
                        if df.empty:
                            logger.error(f"All records failed validation for {tname}. Skipping.")
                            continue
                    else:
                        # Fallback if no contract is defined, fast read via DuckDB
                        df = con.execute("SELECT * FROM read_csv_auto(?)", [raw_path]).df()
                    
                    # Add synthetic PII for testing governance masking
                    if tname == "raw_customers":
                        logger.info(f"Adding synthetic customer PII to {tname}.")
                        df['email'] = df['name'].str.lower().str.replace(' ', '.') + "@example.com"
                        df['phone_number'] = "+1-555-" + df['customer_id'].str[-4:]
                        df['street_address'] = "123 Retail Way, Apt " + df['customer_id'].str[-2:]
                    
                    df.to_parquet(stg_path, index=False)
                    logger.info(f"Converted {files['raw']} to {files['staging']} and loaded into {tname}.")
                    con.execute(f"CREATE OR REPLACE TABLE {tname} AS SELECT * FROM read_parquet(?)", [stg_path])
                    source_used = "CSV (Raw) -> Parquet (Staging)"
                else:
                    logger.warning(f"Neither {stg_path} nor {raw_path} found for {tname}.")
                    continue

                # Count rows
                rows = con.execute(f"SELECT COUNT(*) FROM {tname}").fetchone()[0]
                total_rows += rows
                
                duration = time.time() - ingestion_start
                
                # Log to metadata table
                con.execute("INSERT INTO ingestion_metadata VALUES (?, ?, ?, ?, ?, ?)", 
                            (datetime.now(), tname, 'SUCCESS', source_used, rows, duration))
                
                logger.info(f"Successfully loaded {rows} rows into {tname} in {duration:.2f}s")

            except Exception as e:
                logger.error(f"Failed to ingest {tname}: {e}")
                con.execute("INSERT INTO ingestion_metadata VALUES (?, ?, ?, ?, ?, ?)", 
                            (datetime.now(), tname, 'FAILED', source_used, 0, 0))

        con.close()
        end_time = time.time()
        logger.info(f"--- Ingestion Complete | Total Rows: {total_rows} | Total Time: {end_time - start_time:.2f}s ---")

if __name__ == "__main__":
    ingestor = RetailDataIngestor()
    ingestor.run_ingestion()
