# Premier League Top 6 Prediction - Big Data Platform

Production-ready big data analytics platform for Premier League top 6 predictions using Apache Spark, Kafka, MLflow, and machine learning.

## Architecture Overview

\`\`\`
┌─────────────────────┐
│   Data Sources      │
│ (APIs, CSVs, Kafka)│
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐       ┌──────────────┐
│  Data Ingestion     │──────▶│  Delta Lake  │
│  (Spark Jobs)       │       │  (Storage)   │
└─────────────────────┘       └──────────────┘
           │
           ▼
┌─────────────────────┐
│ Feature Engineering │
│   (Spark SQL)       │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐       ┌──────────────┐
│  ML Training        │──────▶│   MLflow     │
│  (PySpark MLlib)    │       │  (Tracking)  │
└──────────┬──────────┘       └──────────────┘
           │
           ▼
┌─────────────────────┐
│  FastAPI Backend    │
│  (Predictions)      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐       ┌──────────────┐
│  React Dashboard    │──────▶│  WebSockets  │
│  (Visualizations)   │       │  (Real-time) │
└─────────────────────┘       └──────────────┘
           │
           ▼
┌─────────────────────────────────┐
│  Monitoring & Observability     │
│ (Prometheus, Grafana, Logs)    │
└─────────────────────────────────┘
\`\`\`

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.11+
- Git

### Installation

1. **Clone and setup:**
   \`\`\`bash
   git clone <repo-url>
   cd pl-prediction-big-data
   npm run setup
   \`\`\`

2. **Start infrastructure:**
   \`\`\`bash
   npm run dev
   # or for production
   npm run prod
   \`\`\`

3. **Initialize Kafka topics:**
   \`\`\`bash
   npm run init-kafka
   \`\`\`

4. **Access services:**
   - MLflow UI: http://localhost:5000
   - Grafana: http://localhost:3001 (admin/admin)
   - Prometheus: http://localhost:9090
   - FastAPI Docs: http://localhost:8000/docs
   - React Dashboard: http://localhost:3000

## Project Structure

\`\`\`
pl-prediction-big-data/
├── docker-compose.yml          # Main services
├── docker-compose.dev.yml      # Development Spark cluster
├── spark/                      # Spark jobs and streaming
│   ├── jobs/                  # Batch processing jobs
│   │   ├── data_ingestion.py
│   │   ├── feature_engineering.py
│   │   └── model_training.py
│   └── streaming/             # Real-time streaming
│       ├── match_stream_processor.py
│       └── prediction_stream.py
├── api/                        # FastAPI backend
│   ├── main.py                # Application entry
│   ├── requirements.txt
│   ├── app/
│   │   ├── routers/           # API endpoints
│   │   ├── services/          # Business logic
│   │   └── models/            # Data models
│   └── Dockerfile
├── app/                        # Next.js frontend
│   └── page.tsx
├── components/                 # React components
│   ├── dashboard.tsx
│   ├── predictions-table.tsx
│   ├── predictions-chart.tsx
│   └── ...
├── monitoring/                 # Observability
│   ├── prometheus.yml
│   └── grafana/
├── k8s/                        # Kubernetes manifests
└── scripts/                    # Utility scripts
\`\`\`

## Core Technologies

| Component | Technology |
|-----------|-----------|
| Storage | Delta Lake, PostgreSQL |
| Processing | Apache Spark (Batch & Streaming) |
| Messaging | Apache Kafka |
| ML/AI | PySpark MLlib, MLflow |
| API | FastAPI |
| Frontend | React, TypeScript |
| Orchestration | Apache Airflow, Kubernetes |
| Monitoring | Prometheus, Grafana |
| Container | Docker |

## Key Features

- **Distributed Processing**: Spark for large-scale data processing
- **Real-time Streaming**: Kafka + Spark Structured Streaming
- **ML Pipeline**: Automated training with MLflow
- **RESTful API**: FastAPI with WebSocket support
- **Interactive Dashboard**: React with real-time updates
- **Production Ready**: Docker, Kubernetes, monitoring
- **Scalable**: Horizontal scaling with Kubernetes

## Usage Examples

### Make a Prediction

\`\`\`bash
curl -X POST http://localhost:8000/api/v1/predictions/predict/top6 \
  -H "Content-Type: application/json" \
  -d '{
    "team_name": "Manchester City",
    "avg_xg": 2.1,
    "avg_goals": 1.8,
    "total_assists": 45,
    "squad_depth": 23,
    "win_ratio": 0.75,
    "xg_difference": 0.3,
    "defensive_rating": 15.2
  }'
\`\`\`

### Get Current Predictions

\`\`\`bash
curl http://localhost:8000/api/v1/predictions/current-season
\`\`\`

### Trigger Model Training

\`\`\`bash
curl -X POST http://localhost:8000/api/v1/predictions/trigger-training
\`\`\`

## Development

### Run locally with hot reload:

\`\`\`bash
npm run dev
\`\`\`

### Access development services:
- Spark Master: http://localhost:8080
- Kafka UI: http://localhost:9000 (if using Kafdrop)

## Deployment

### Kubernetes Deployment

\`\`\`bash
# Create namespace
kubectl create namespace pl-prediction

# Deploy services
kubectl apply -f k8s/

# Check status
kubectl get pods -n pl-prediction
\`\`\`

### Docker Compose Production

\`\`\`bash
npm run prod
npm run logs  # View logs
\`\`\`

## Monitoring

- **Prometheus**: http://localhost:9090 (metrics)
- **Grafana**: http://localhost:3001 (dashboards)
- **MLflow**: http://localhost:5000 (model tracking)

## Performance Tuning

### Spark Configuration
\`\`\`yaml
spark.executor.memory: 8g
spark.driver.memory: 4g
spark.sql.adaptive.enabled: true
spark.shuffle.partitions: 200
\`\`\`

### Kafka Performance
\`\`\`yaml
num.partitions: 8
replication.factor: 3
compression.type: snappy
\`\`\`

## Troubleshooting

### Services not starting
\`\`\`bash
# Clean up and restart
docker-compose down -v
npm run prod
\`\`\`

### Out of memory
\`\`\`bash
# Increase Docker memory limits
# Edit docker-compose.yml or system settings
\`\`\`

### Kafka connection issues
\`\`\`bash
# Check Kafka logs
docker logs kafka
# Verify broker is healthy
docker-compose logs kafka
\`\`\`

## Contributing

1. Create a feature branch
2. Make changes
3. Test thoroughly
4. Submit PR

## License

MIT

## Support

For issues or questions, open an issue on GitHub or contact the team.

---

**Built with ❤️ for Premier League analytics**
