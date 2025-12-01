from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import mlflow
from prometheus_client import Counter, Histogram, generate_latest
import time

# Import routers
from app.routers import predictions, teams, players, analytics
from app.services.db import init_db
from app.services.kafka_producer import KafkaProducerService
from app.middleware.metrics import setup_metrics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Metrics
prediction_requests = Counter(
    'prediction_requests_total',
    'Total prediction requests',
    ['endpoint', 'status']
)
prediction_latency = Histogram(
    'prediction_latency_seconds',
    'Prediction request latency',
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting up application...")
    init_db()
    mlflow.set_tracking_uri("http://mlflow:5000")
    logger.info("Application startup complete")
    yield
    # Shutdown
    logger.info("Shutting down application...")

app = FastAPI(
    title="Premier League Prediction Platform",
    version="2.0.0",
    description="Big Data ML Platform for PL Top 6 Predictions",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(predictions.router, prefix="/api/v1/predictions", tags=["predictions"])
app.include_router(teams.router, prefix="/api/v1/teams", tags=["teams"])
app.include_router(players.router, prefix="/api/v1/players", tags=["players"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["analytics"])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0"
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Premier League Prediction Platform",
        "version": "2.0.0",
        "docs": "/docs",
        "health": "/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        workers=4
    )
