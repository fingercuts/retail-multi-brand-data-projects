# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    make \
    && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install dbt dependencies
RUN cd dbt_project && dbt deps

# Expose ports for Streamlit and Airflow
EXPOSE 8501 8080

# Environment variables
ENV PYTHONUNBUFFERED=1
ENV DBT_PROFILES_DIR=/app/dbt_project

# Default command (can be overridden by docker-compose)
CMD ["make", "help"]
