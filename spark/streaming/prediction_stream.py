from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, from_json, udf, current_timestamp, json_tuple
)
from pyspark.sql.types import StructType, StructField, StringType, DoubleType
import mlflow.pyfunc
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PredictionStream:
    def __init__(self, spark_master_url="local", kafka_broker="kafka:9092", mlflow_uri="http://mlflow:5000"):
        self.spark = SparkSession.builder \
            .appName("PredictionStream") \
            .master(spark_master_url) \
            .getOrCreate()
        
        self.kafka_broker = kafka_broker
        mlflow.set_tracking_uri(mlflow_uri)
        self.model = mlflow.pyfunc.load_model("models:/pl_top6_model/production")
        self.spark.sparkContext.setLogLevel("INFO")

    def create_schema(self):
        """Schema for incoming stat updates"""
        return StructType([
            StructField("team_name", StringType()),
            StructField("avg_xg", DoubleType()),
            StructField("avg_goals", DoubleType()),
            StructField("total_assists", DoubleType()),
            StructField("squad_depth", DoubleType()),
            StructField("win_ratio", DoubleType()),
            StructField("xg_difference", DoubleType()),
            StructField("defensive_rating", DoubleType()),
            StructField("timestamp", StringType())
        ])

    def read_stats_stream(self, topic: str = "real_time_stats"):
        """Read team stats updates from Kafka"""
        schema = self.create_schema()
        
        df = self.spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", self.kafka_broker) \
            .option("subscribe", topic) \
            .load()
        
        parsed_df = df \
            .select(from_json(col("value").cast("string"), schema).alias("data")) \
            .select("data.*")
        
        return parsed_df

    def make_predictions(self, df):
        """Make predictions on streaming data"""
        
        def predict_batch(stats):
            try:
                df_pred = pd.DataFrame([{
                    'avg_xg': stats['avg_xg'],
                    'avg_goals': stats['avg_goals'],
                    'total_assists': stats['total_assists'],
                    'squad_depth': stats['squad_depth'],
                    'win_ratio': stats['win_ratio'],
                    'xg_difference': stats['xg_difference'],
                    'defensive_rating': stats['defensive_rating'],
                }])
                
                prediction = self.model.predict(df_pred)[0]
                probability = self.model.predict_proba(df_pred)[0][1] if hasattr(self.model, 'predict_proba') else 0.5
                
                return {
                    'prediction': int(prediction),
                    'probability': float(probability),
                    'confidence': f"{probability * 100:.1f}%"
                }
            except Exception as e:
                logger.error(f"Prediction error: {str(e)}")
                return {'prediction': 0, 'probability': 0.0, 'confidence': '0%'}
        
        # Register UDF
        predict_udf = udf(predict_batch)
        
        predictions_df = df \
            .withColumn(
                "prediction_result",
                predict_udf(
                    col("avg_xg"), col("avg_goals"), col("total_assists"),
                    col("squad_depth"), col("win_ratio"), col("xg_difference"),
                    col("defensive_rating")
                )
            ) \
            .select(
                col("team_name"),
                col("prediction_result.prediction").alias("top_6_prediction"),
                col("prediction_result.probability").alias("probability"),
                col("prediction_result.confidence").alias("confidence"),
                current_timestamp().alias("prediction_timestamp")
            )
        
        return predictions_df

    def write_predictions(self, df):
        """Write predictions to Kafka and Delta Lake"""
        query = df \
            .writeStream \
            .format("delta") \
            .mode("append") \
            .option("checkpointLocation", "/tmp/prediction_checkpoint") \
            .start("/data/processed/streaming_predictions")
        
        return query

    def process(self):
        """Main streaming prediction pipeline"""
        try:
            # Read stats stream
            stats_stream = self.read_stats_stream()
            
            # Make predictions
            predictions = self.make_predictions(stats_stream)
            
            # Write results
            query = self.write_predictions(predictions)
            
            # Wait for termination
            self.spark.streams.awaitAnyTermination()
            
        except Exception as e:
            logger.error(f"Error in prediction stream: {str(e)}")
            raise

def main():
    stream = PredictionStream(
        spark_master_url="spark://spark-master:7077",
        kafka_broker="kafka:9092",
        mlflow_uri="http://mlflow:5000"
    )
    stream.process()

if __name__ == "__main__":
    main()
