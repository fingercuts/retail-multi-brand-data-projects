# Retail Multi-Brand Data Project: User Manual

This repository contains the end-to-end data pipeline for the Retail Multi-Brand project, including ingestion, dbt transformations, and a Streamlit monitoring dashboard.

## Quick Start

The project uses a [Makefile](../Makefile) to wrap complex commands.

### Prerequisites: `make`
Windows users usually need to install `make` manually:
- **Chocolatey**: `choco install make`
- **Scoop**: `scoop install make`
- Or use **Git Bash** / **WSL**.

### Run Everything (First-Time Setup)
From the project root:

1.  **Environment**: `make setup` (Installs deps and dbt packages)
2.  **Ingestion**: `make ingest` (CSVs -> DuckDB)
3.  **Transform**: `make dbt-build` (Runs models and tests)
4.  **Launch Dashboard**: `make dashboard`

---

## Makefile Reference

| Command | Action |
| :--- | :--- |
| `make setup` | Install Python requirements and dbt deps |
| `make ingest` | Standard Python ingestion script |
| `make ingest-spark` | Spark-based ingestion for larger datasets |
| `make ingest-stream`| Simulates real-time stream ingestion |
| `make dbt-build` | Full dbt build (models + tests) |
| `make dashboard` | Open Streamlit UI |
| `make docker-up` | Spin up Postgres (for serving layer) |
| `make serve` | Sync DuckDB -> Postgres |
| `make api` | Start the FastAPI service |
| `make quality-report`| Run data quality checks |
| `make docs` | Generate and host dbt documentation |

---

## 1. Project Architecture

The pipeline follows a standard Medallion structure:

1.  **Raw (`data/raw`)**: Source CSVs.
2.  **Staging (`data/staging`)**: Converted to Parquet for performance.
3.  **Marts (DuckDB)**: Final Star Schema calculated via dbt.

---

## 2. Pipeline Details

### Environment Setup
Run `.\setup_env.ps1` if you aren't using `make`. This creates the `.venv` and installs everything in `requirements.txt`.

### Ingestion Logic
The `scripts/ingest_data.py` script handles the initial load into DuckDB. It prioritizes Parquet files in the staging area if available, otherwise it falls back to raw CSVs.

### dbt Transformations
Models are located in the `dbt_project` directory.
- `dbt run`: Builds the tables.
- `dbt test`: Validates data (uniqueness, nulls, etc.).
- **Note**: The pipeline builds `stg_` models before `fct_` models based on the dbt dependency graph.

### Orchestration
Airflow DAGs are defined in `airflow/retail_pipeline.py`. It automates the `Ingest` -> `dbt Run` -> `dbt Test` flow. Pathing is handled dynamically relative to the project root.

---

## 3. Databases & API

### DuckDB vs. Postgres
- **DuckDB**: Used for local analytical processing and dbt transformations.
- **Postgres**: Serving layer for the API and Streamlit dashboard.

To sync data between them:
1. `make docker-up`
2. `make serve`
3. `make api` (FastAPI accessible at port 8000)

---

## 4. Manual Debugging

To query the database directly via Python:
```python
import duckdb
con = duckdb.connect('data/multibrand_retail.duckdb')
print(con.execute("SELECT * FROM fct_sales LIMIT 5").df())
```

---

## 5. Troubleshooting

| Issue | Fix |
| :--- | :--- |
| **Command not found** | Activate the venv: `.venv\Scripts\activate` |
| **Pathing errors** | Always run commands from the project root |
| **Database is locked** | Ensure only one process is connected to the `.duckdb` file |

---

## 6. Access Control & PII
- Customer data (names, emails) is masked at the staging level.
- Use `dim_customers` for general analytics.
- `dim_customers_authorized` is restricted for sensitive lookups.
