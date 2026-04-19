# Use the official Apache Airflow image as the base
FROM apache/airflow:2.8.1-python3.10

# Switch to root to install system-level dependencies if needed
USER root
RUN apt-get update \
  && apt-get install -y --no-install-recommends \
         build-essential \
  && apt-get autoremove -yqq --purge \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# Switch back to the airflow user
USER airflow

# Copy requirements
COPY requirements.txt /requirements.txt

# Install Python packages (dbt, duckdb, pandas) required by tasks
RUN pip install --no-cache-dir -r /requirements.txt
