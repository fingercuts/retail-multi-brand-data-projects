# Software Requirements and Dependencies

This project is built using a modern Python data stack. Dependencies are managed via `requirements.txt` for the core environment and `packages.yml` for dbt extensions.

## Dependency Overview

### Data Processing & Transformation
- **duckdb**: Core OLAP engine for local data warehousing.
- **dbt-core & dbt-duckdb**: Transformation and modeling framework.
- **pandas & pyarrow**: High-performance data manipulation and Parquet support.
- **pyspark**: Distributed processing engine for large-scale historical loads.

### Application & API Layer
- **fastapi**: High-performance web framework for the serving layer.
- **uvicorn**: ASGI server for production-grade API hosting.
- **sqlalchemy**: SQL toolkit and Object Relational Mapper (ORM).
- **streamlit**: Framework for the interactive analytical dashboard.

### Analytics & Forecasting
- **prophet**: Time-series forecasting model for demand planning.
- **plotly & matplotlib**: Visualization libraries for reporting.

### Orchestration & Infrastructure
- **apache-airflow**: Programmatic workflow orchestration and scheduling.
- **psycopg2-binary**: PostgreSQL adapter for operational database connectivity.

---

## Environment Setup
To initialize the software environment:

1. **Python Version**: Recommended Python 3.9+ 
2. **Installation**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Database Initialization**: 
   Ensure you have Docker installed to run the PostgreSQL container via `docker-compose up`.
