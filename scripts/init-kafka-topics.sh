#!/bin/bash

# Wait for Kafka to be ready
sleep 10

# Create topics
docker exec kafka kafka-topics --create \
  --topic match_events_stream \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1 \
  --if-not-exists

docker exec kafka kafka-topics --create \
  --topic player_performance_updates \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1 \
  --if-not-exists

docker exec kafka kafka-topics --create \
  --topic predictions_stream \
  --bootstrap-server localhost:9092 \
  --partitions 3 \
  --replication-factor 1 \
  --if-not-exists

docker exec kafka kafka-topics --create \
  --topic injury_reports \
  --bootstrap-server localhost:9092 \
  --partitions 2 \
  --replication-factor 1 \
  --if-not-exists

echo "Kafka topics created successfully!"
