import duckdb
import os
import pandas as pd
from tabulate import tabulate

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'multibrand_retail.duckdb')

def generate_quality_report():
    if not os.path.exists(DB_PATH):
        print("Error: Database not found. Please run the ingestion scripts first.")
        return

    con = duckdb.connect(DB_PATH, read_only=True)
    
    print("\n" + "="*50)
    print("DATA PIPELINE HEALTH REPORT")
    print("="*50)

    # 1. Row Counts (Pipeline Volume)
    print("\n[Audit] Layer Volume Summary")
    tables = ['stg_sales', 'stg_customers', 'fact_sales', 'dim_customers']
    counts = []
    for t in tables:
        try:
            count = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            counts.append({"Entity": t, "Record Count": f"{count:,}"})
        except:
            counts.append({"Entity": t, "Record Count": "TABLE NOT FOUND"})
    
    print(tabulate(counts, headers="keys", tablefmt="pretty"))

    # 2. Cleansing Efficiency (Fact Sales)
    print("\n[Compliance] PII Masking Verification")
    try:
        pii_check = con.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(email_hash) as emails_hashed,
                COUNT(phone_preview) as phones_masked
            FROM dim_customers
        """).df()
        print(tabulate(pii_check, headers="keys", tablefmt="pretty"))
    except Exception as e:
        print(f"PII Check Failed: {e}")

    # 3. Integrity Checks
    print("\n[Integrity] Null Key Detection (Marts)")
    null_report = []
    marts = [('fact_sales', 'transaction_id'), ('dim_customers', 'customer_id'), ('dim_products', 'product_id')]
    for table, pk in marts:
        try:
            nulls = con.execute(f"SELECT COUNT(*) FROM {table} WHERE {pk} IS NULL").fetchone()[0]
            null_report.append({"Table": table, "NULL Primary Keys": nulls})
        except:
            pass
    
    print(tabulate(null_report, headers="keys", tablefmt="pretty"))
    
    print("\n" + "="*50)
    print("REPORT COMPLETE")
    print("="*50 + "\n")
    con.close()

if __name__ == "__main__":
    generate_quality_report()
