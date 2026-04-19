from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Dynamically calculate the project root directory relative to this file
# This ensures portability across different user local paths
DAG_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(DAG_DIR)

DBT_PROJECT_DIR = os.path.join(BASE_DIR, "dbt_project")
DBT_PROFILES_DIR = DBT_PROJECT_DIR
INGEST_SCRIPT = os.path.join(BASE_DIR, "scripts", "ingest_data.py")

with DAG(
    'retail_multi_brand_pipeline',
    default_args=default_args,
    description='End-to-end retail data pipeline',
    schedule_interval=timedelta(days=1),
    catchup=False,
) as dag:

    # task 1: Ingestion
    ingest_data = BashOperator(
        task_id='ingest_data',
        bash_command=f'python "{INGEST_SCRIPT}"',
    )

    # task 2: dbt Run
    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command=f'dbt run --project-dir "{DBT_PROJECT_DIR}" --profiles-dir "{DBT_PROFILES_DIR}"',
    )

    # task 3: dbt Test
    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command=f'dbt test --project-dir "{DBT_PROJECT_DIR}" --profiles-dir "{DBT_PROFILES_DIR}"',
    )

    ingest_data >> dbt_run >> dbt_test
