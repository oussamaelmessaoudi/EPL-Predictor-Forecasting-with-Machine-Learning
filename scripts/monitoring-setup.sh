#!/bin/bash

echo "Setting up monitoring and observability..."

# Create monitoring namespace
kubectl create namespace monitoring || true

# Install Prometheus Operator
kubectl apply -f https://github.com/prometheus-operator/prometheus-operator/releases/download/v0.68.0/bundle.yaml

# Wait for operator to be ready
kubectl wait --for=condition=available --timeout=300s deployment/prometheus-operator -n default

# Apply Prometheus configuration
kubectl apply -f monitoring/prometheus.yml

# Create Prometheus service
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: prometheus
  namespace: pl-prediction
spec:
  selector:
    app: prometheus
  ports:
  - port: 9090
    targetPort: 9090
  type: LoadBalancer
EOF

# Create Grafana service
kubectl apply -f - <<EOF
apiVersion: v1
kind: Service
metadata:
  name: grafana
  namespace: pl-prediction
spec:
  selector:
    app: grafana
  ports:
  - port: 3000
    targetPort: 3000
  type: LoadBalancer
EOF

echo "Monitoring setup complete!"
echo "Access Grafana at: http://localhost:3000"
echo "Access Prometheus at: http://localhost:9090"
