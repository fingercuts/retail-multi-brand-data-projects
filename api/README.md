# Serving Layer: Retail Data API

This directory contains the FastAPI application responsible for serving analytical and operational data from the PostgreSQL serving database.

## Overview
The API acts as the primary interface for downstream applications to consume cleaned and governed retail data. It interacts with the **Serving Layer** (PostgreSQL), which is populated during the reverse-ETL phase of the pipeline.

## Setup & Execution

### 1. Start Infrastructure
Ensure the PostgreSQL container is running:
```bash
make docker-up
```

### 2. Synchronization
If you haven't synced data from DuckDB to PostgreSQL, run:
```bash
make serve
```

### 3. Run the API
Start the Uvicorn server:
```bash
make api
```

The service will be available at `http://localhost:8000`.

## Documentation
FastAPI provides automatic interactive documentation:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **Redoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Core Documentation
- **Customers**: Returns masked customer profiles (GDPR compliant).
- **Sales**: Returns aggregated transaction records for operational reporting.
- **Health**: System connectivity status.
