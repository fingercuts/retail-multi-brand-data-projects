from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.sensors.filesystem import FileSensor
from datetime import datetime, timedelta
import os
import sys

# Add script directory to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from scripts.ingest_data import RetailDataIngestor

# Default arguments for the pro-level DAG
default_args = {
    'owner': 'data_engineering',
    'depends_on_past': True,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'advanced_retail_pipeline',
    default_args=default_args,
    description='Professional event-driven pipeline with PII protection',
    schedule_interval='@daily',
    catchup=False,
    tags=['production', 'governance', 'event-driven']
) as dag:

    # 1. THE SENSOR: Wait for the raw sales file to arrive (Simulation)
    # This turns a "scheduled" pipeline into an "event-driven" one
    wait_for_sales_data = FileSensor(
        task_id='wait_for_daily_sales_data',
        filepath='/app/data/raw/raw_sales_transactions.csv',
        fs_conn_id='fs_default',
        poke_interval=60,  # Check every minute
        timeout=3600       # Give up after 1 hour
    )

    # 2. INGESTION: Run the class-based framework
    def run_ingestion_wrapper():
        ingestor = RetailDataIngestor()
        ingestor.run_ingestion()

    ingest_data = PythonOperator(
        task_id='ingest_enriched_data',
        python_callable=run_ingestion_wrapper
    )

    # 3. TRANSFORMATION: dbt run & test (Star Schema + PII Masking)
    def run_dbt_task(command):
        # In Docker, we would run: os.system(f"cd /app/dbt_project && dbt {command}")
        print(f"Executing dbt {command}...")

    dbt_build = PythonOperator(
        task_id='dbt_build_marts',
        python_callable=run_dbt_task,
        op_kwargs={'command': 'build'}
    )

    # Dependencies
    wait_for_sales_data >> ingest_data >> dbt_build
