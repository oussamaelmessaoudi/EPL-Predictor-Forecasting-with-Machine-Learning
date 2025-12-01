from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, from_json, current_timestamp, window,
    avg, sum as spark_sum, count, max as spark_max, min as spark_min
)
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, IntegerType
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataIngestionPipeline:
    def __init__(self, spark_master_url="local"):
        self.spark = SparkSession.builder \
            .appName("PLDataIngestion") \
            .master(spark_master_url) \
            .config("spark.sql.shuffle.partitions", "8") \
            .config("spark.default.parallelism", "8") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("INFO")

    def load_match_data(self, source_path: str):
        """Load historical match data from CSV"""
        try:
            df = self.spark.read \
                .option("header", "true") \
                .option("inferSchema", "true") \
                .csv(source_path)
            
            logger.info(f"Loaded {df.count()} match records from {source_path}")
            return df
        except Exception as e:
            logger.error(f"Error loading match data: {str(e)}")
            raise

    def load_player_stats(self, source_path: str):
        """Load player statistics from CSV"""
        try:
            df = self.spark.read \
                .option("header", "true") \
                .option("inferSchema", "true") \
                .csv(source_path)
            
            logger.info(f"Loaded {df.count()} player records from {source_path}")
            return df
        except Exception as e:
            logger.error(f"Error loading player data: {str(e)}")
            raise

    def ingest_kafka_stream(self, broker_servers: str, topic: str):
        """Ingest real-time data from Kafka"""
        schema = StructType([
            StructField("match_id", StringType()),
            StructField("team_name", StringType()),
            StructField("opponent", StringType()),
            StructField("xg", DoubleType()),
            StructField("goals", DoubleType()),
            StructField("possession", DoubleType()),
            StructField("timestamp", StringType())
        ])
        
        df = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", broker_servers) \
            .option("subscribe", topic) \
            .option("startingOffsets", "latest") \
            .load() \
            .select(from_json(col("value").cast("string"), schema).alias("data")) \
            .select("data.*")
        
        logger.info(f"Created Kafka stream from topic: {topic}")
        return df

    def save_to_delta(self, df, path: str, mode: str = "overwrite"):
        """Save DataFrame to Delta Lake format"""
        try:
            df.write \
                .format("delta") \
                .mode(mode) \
                .save(path)
            logger.info(f"Saved data to Delta Lake: {path}")
        except Exception as e:
            logger.error(f"Error saving to Delta Lake: {str(e)}")
            raise

def main():
    pipeline = DataIngestionPipeline(spark_master_url="spark://spark-master:7077")
    
    # Load historical data
    matches_df = pipeline.load_match_data("/data/raw/match_data.csv")
    players_df = pipeline.load_player_stats("/data/raw/player_stats.csv")
    
    # Save to Delta Lake
    pipeline.save_to_delta(matches_df, "/data/processed/matches_delta")
    pipeline.save_to_delta(players_df, "/data/processed/players_delta")
    
    logger.info("Data ingestion pipeline completed successfully")

if __name__ == "__main__":
    main()
