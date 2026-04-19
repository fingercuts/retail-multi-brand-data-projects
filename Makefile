.PHONY: setup ingest dbt-build dashboard docs help test lint

help:
	@echo "OmniRetail Pipeline Management"
	@echo ""
	@echo "Available commands:"
	@echo "  setup          - Install dependencies and initializes environment"
	@echo "  ingest         - Execute batch ingestion (CSV -> Parquet -> DuckDB)"
	@echo "  ingest-spark   - Execute PySpark-based batch ingestion"
	@echo "  ingest-stream  - Start PySpark streaming ingestion"
	@echo "  dbt-build      - Build and test analytical models"
	@echo "  serve          - Run reverse-ETL to PostgreSQL serving layer"
	@echo "  api            - Start the FastAPI serving layer"
	@echo "  dashboard      - Launch the Streamlit analytical dashboard"
	@echo "  quality-report - Generate data health and volume audit"
	@echo "  test           - Run Python unit and integration tests (pytest)"
	@echo "  lint           - Run code style and SQL formatting checks"
	@echo "  docs           - Generate and serve dbt documentation"
	@echo "  clean          - Remove generated local database and logs"

setup:
	pip install -r requirements.txt
	cd dbt_project && dbt deps

ingest:
	python scripts/ingest_data.py

ingest-spark:
	python scripts/ingest_data_spark.py

ingest-stream:
	python scripts/stream_ingestion.py

serve:
	python scripts/serve_data.py

api:
	uvicorn api.main:app --reload

quality-report:
	python scripts/quality_report.py

dbt-build:
	cd dbt_project && dbt build

test:
	pytest tests/

lint:
	pre-commit run --all-files
	cd dbt_project && sqlfluff lint models --dialect duckdb

dashboard:
	streamlit run dashboards/Home.py

docker-up:
	docker-compose up --build

ingest-logs:
	cat ingestion_details.log

notebooks:
	jupyter lab

docs:
	cd dbt_project && dbt docs generate && dbt docs serve

clean:
	@echo "Cleaning artifacts..."
	@if exist ingestion_details.log del ingestion_details.log
	@if exist data\multibrand_retail.duckdb del data\multibrand_retail.duckdb
	@if exist data\multibrand_retail.duckdb.wal del data\multibrand_retail.duckdb.wal
	@if exist dbt_project\target rmdir /s /q dbt_project\target
	@if exist dbt_project\dbt_packages rmdir /s /q dbt_project\dbt_packages
	@if exist .venv rmdir /s /q .venv

reset: clean setup
	@echo "Environment reset successful."
