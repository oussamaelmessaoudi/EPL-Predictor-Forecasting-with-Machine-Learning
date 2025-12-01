from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, from_json, current_timestamp, window,
    avg, sum as spark_sum, count
)
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MatchStreamProcessor:
    def __init__(self, spark_master_url="local", kafka_broker="kafka:9092"):
        self.spark = SparkSession.builder \
            .appName("MatchStreamProcessor") \
            .master(spark_master_url) \
            .config("spark.streaming.kafka.maxRatePerPartition", "1000") \
            .getOrCreate()
        
        self.kafka_broker = kafka_broker
        self.spark.sparkContext.setLogLevel("INFO")

    def create_schema(self):
        """Define the schema for incoming match events"""
        return StructType([
            StructField("match_id", StringType()),
            StructField("team_name", StringType()),
            StructField("opponent", StringType()),
            StructField("xg", DoubleType()),
            StructField("goals", DoubleType()),
            StructField("possession", DoubleType()),
            StructField("shots", IntegerType()),
            StructField("shots_on_target", IntegerType()),
            StructField("timestamp", StringType())
        ])

    def read_match_stream(self, topic: str = "match_events_stream"):
        """Read streaming match data from Kafka"""
        schema = self.create_schema()
        
        df = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self.kafka_broker) \
            .option("subscribe", topic) \
            .option("startingOffsets", "latest") \
            .option("failOnDataLoss", "false") \
            .load()
        
        # Parse JSON
        parsed_df = df \
            .select(from_json(col("value").cast("string"), schema).alias("data")) \
            .select("data.*")
        
        logger.info(f"Started reading from Kafka topic: {topic}")
        return parsed_df

    def aggregate_match_stats(self, df):
        """Aggregate match statistics in 5-minute windows"""
        aggregated = df \
            .withColumn("event_time", col("timestamp").cast("timestamp")) \
            .groupBy(
                window(col("event_time"), "5 minutes", "1 minute"),
                col("team_name")
            ) \
            .agg(
                avg("xg").alias("avg_xg"),
                spark_sum("goals").alias("total_goals"),
                avg("possession").alias("avg_possession"),
                spark_sum("shots").alias("total_shots"),
                spark_sum("shots_on_target").alias("shots_on_target"),
                count("match_id").alias("events_count")
            ) \
            .select(
                col("window.start").alias("window_start"),
                col("window.end").alias("window_end"),
                col("team_name"),
                col("avg_xg"),
                col("total_goals"),
                col("avg_possession"),
                col("total_shots"),
                col("shots_on_target"),
                col("events_count"),
                current_timestamp().alias("processed_at")
            )
        
        return aggregated

    def write_to_console(self, df):
        """Write to console for debugging"""
        query = df \
            .writeStream \
            .format("console") \
            .option("truncate", "false") \
            .start()
        
        return query

    def write_to_delta(self, df, path: str):
        """Write streaming results to Delta Lake"""
        query = df \
            .writeStream \
            .format("delta") \
            .mode("append") \
            .option("checkpointLocation", f"{path}_checkpoint") \
            .option("mergeSchema", "true") \
            .start(path)
        
        logger.info(f"Started writing stream to Delta Lake: {path}")
        return query

    def write_to_kafka(self, df, topic: str):
        """Write processed data back to Kafka"""
        query = df \
            .select(col("*").cast("string")) \
            .writeStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self.kafka_broker) \
            .option("topic", topic) \
            .option("checkpointLocation", f"/tmp/kafka_checkpoint_{topic}") \
            .start()
        
        logger.info(f"Started writing stream to Kafka topic: {topic}")
        return query

    def process(self):
        """Main processing pipeline"""
        try:
            # Read from Kafka
            match_stream = self.read_match_stream()
            
            # Aggregate statistics
            aggregated = self.aggregate_match_stats(match_stream)
            
            # Write to multiple sinks
            query_console = self.write_to_console(aggregated)
            query_delta = self.write_to_delta(aggregated, "/data/processed/real_time_stats")
            query_kafka = self.write_to_kafka(aggregated, "predictions_stream")
            
            # Wait for queries
            self.spark.streams.awaitAnyTermination()
            
        except Exception as e:
            logger.error(f"Error in stream processing: {str(e)}")
            raise

def main():
    processor = MatchStreamProcessor(
        spark_master_url="spark://spark-master:7077",
        kafka_broker="kafka:9092"
    )
    processor.process()

if __name__ == "__main__":
    main()
