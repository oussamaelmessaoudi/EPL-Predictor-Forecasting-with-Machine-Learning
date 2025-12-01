#!/bin/bash
set -e

echo "Setting up Premier League Big Data Platform..."

# Create necessary directories
mkdir -p spark/jobs
mkdir -p spark/streaming
mkdir -p spark/utils
mkdir -p api/app/routers
mkdir -p api/app/models
mkdir -p api/app/services
mkdir -p frontend/src/components
mkdir -p frontend/src/services
mkdir -p monitoring/grafana/provisioning/dashboards
mkdir -p monitoring/grafana/provisioning/datasources

# Copy environment file
cp .env.example .env

# Create Kafka topics
chmod +x scripts/init-kafka-topics.sh

echo "Setup complete! Run 'docker-compose up -d' to start services."
