from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, start_http_server
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create registry
registry = CollectorRegistry()

# Define metrics
prediction_requests = Counter(
    'prediction_requests_total',
    'Total prediction requests',
    ['endpoint', 'status'],
    registry=registry
)

prediction_latency = Histogram(
    'prediction_latency_seconds',
    'Prediction request latency in seconds',
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 2.0, 5.0],
    registry=registry
)

model_accuracy = Gauge(
    'model_accuracy',
    'Current model accuracy score',
    registry=registry
)

training_job_status = Gauge(
    'training_job_status',
    'Training job status (0=failed, 1=running, 2=success)',
    registry=registry
)

kafka_consumer_lag = Gauge(
    'kafka_consumer_lag',
    'Kafka consumer lag in messages',
    ['topic', 'partition'],
    registry=registry
)

spark_job_duration = Histogram(
    'spark_job_duration_seconds',
    'Spark job execution duration',
    registry=registry
)

active_predictions = Gauge(
    'active_predictions',
    'Number of active predictions being computed',
    registry=registry
)

def track_prediction(func):
    """Decorator to track prediction metrics"""
    def wrapper(*args, **kwargs):
        start = time.time()
        endpoint = kwargs.get('endpoint', 'unknown')
        try:
            result = func(*args, **kwargs)
            prediction_requests.labels(endpoint=endpoint, status='success').inc()
            return result
        except Exception as e:
            prediction_requests.labels(endpoint=endpoint, status='error').inc()
            logger.error(f"Prediction error: {str(e)}")
            raise
        finally:
            latency = time.time() - start
            prediction_latency.observe(latency)
            logger.info(f"Prediction completed in {latency:.3f}s")
    
    return wrapper

def start_metrics_server(port=8001):
    """Start Prometheus metrics server"""
    try:
        start_http_server(port, registry=registry)
        logger.info(f"Metrics server started on port {port}")
    except Exception as e:
        logger.error(f"Error starting metrics server: {str(e)}")
