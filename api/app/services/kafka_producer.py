from kafka import KafkaProducer
import json
import logging

logger = logging.getLogger(__name__)

class KafkaProducerService:
    def __init__(self, bootstrap_servers="kafka:9092"):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            logger.info("Kafka producer initialized")
        except Exception as e:
            logger.error(f"Error initializing Kafka producer: {str(e)}")
            self.producer = None

    def send_event(self, topic: str, event: dict):
        """Send event to Kafka topic"""
        if self.producer is None:
            logger.warning(f"Cannot send event to {topic}: producer not initialized")
            return
        
        try:
            self.producer.send(topic, value=event)
            self.producer.flush()
            logger.info(f"Event sent to topic: {topic}")
        except Exception as e:
            logger.error(f"Error sending event to Kafka: {str(e)}")

    def close(self):
        """Close producer"""
        if self.producer:
            self.producer.close()
