#!/bin/bash

# Deploy Airflow for orchestration
echo "Setting up Apache Airflow..."

# Create Airflow directories
mkdir -p airflow/logs airflow/plugins airflow/dags

# Set Airflow home
export AIRFLOW_HOME=$(pwd)/airflow

# Install Airflow with required providers
pip install apache-airflow apache-airflow-providers-apache-spark \
    apache-airflow-providers-postgres \
    apache-airflow-providers-http

# Initialize Airflow database
airflow db init

# Create admin user
airflow users create \
    --username admin \
    --firstname Admin \
    --lastname User \
    --role Admin \
    --email admin@example.com \
    --password admin

echo "Airflow setup complete!"
