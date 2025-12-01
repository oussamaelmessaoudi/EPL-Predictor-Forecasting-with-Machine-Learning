from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.classification import RandomForestClassifier, GBTClassifier
from pyspark.ml.evaluation import BinaryClassificationEvaluator, MulticlassClassificationEvaluator
from pyspark.mllib.evaluation import BinaryClassificationMetrics
import mlflow
import mlflow.spark
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ModelTrainingPipeline:
    def __init__(self, spark_master_url="local", mlflow_uri="http://mlflow:5000"):
        self.spark = SparkSession.builder \
            .appName("PLModelTraining") \
            .master(spark_master_url) \
            .getOrCreate()
        
        mlflow.set_tracking_uri(mlflow_uri)
        mlflow.set_experiment("pl_top6_prediction")
        self.spark.sparkContext.setLogLevel("INFO")

    def read_training_data(self, path: str):
        """Read training data from Delta Lake"""
        df = self.spark.read.format("delta").load(path)
        logger.info(f"Loaded {df.count()} training samples")
        return df

    def split_data(self, df, train_ratio=0.8):
        """Split data into train and test sets"""
        train_df, test_df = df.randomSplit([train_ratio, 1 - train_ratio], seed=42)
        logger.info(f"Train: {train_df.count()}, Test: {test_df.count()}")
        return train_df, test_df

    def build_pipeline(self, feature_cols):
        """Build ML pipeline"""
        # Feature assembly
        assembler = VectorAssembler(
            inputCols=feature_cols,
            outputCol="features",
            handleInvalid="skip"
        )
        
        # Feature scaling
        scaler = StandardScaler(
            inputCol="features",
            outputCol="scaled_features",
            withMean=True,
            withStd=True
        )
        
        # Random Forest Classifier
        rf = RandomForestClassifier(
            labelCol="top_6_label",
            featuresCol="scaled_features",
            numTrees=200,
            maxDepth=12,
            minInstancesPerNode=5,
            seed=42
        )
        
        pipeline = Pipeline(stages=[assembler, scaler, rf])
        logger.info("Built ML pipeline with Random Forest")
        return pipeline

    def train_model(self, train_df, test_df, pipeline):
        """Train model and log metrics"""
        with mlflow.start_run(run_name="rf_top6_v2"):
            # Log parameters
            mlflow.log_param("num_trees", 200)
            mlflow.log_param("max_depth", 12)
            mlflow.log_param("min_instances_per_node", 5)
            mlflow.log_param("training_samples", train_df.count())
            mlflow.log_param("test_samples", test_df.count())
            
            # Train model
            logger.info("Starting model training...")
            model = pipeline.fit(train_df)
            logger.info("Model training completed")
            
            # Make predictions
            predictions = model.transform(test_df)
            
            # Evaluate model
            evaluator = BinaryClassificationEvaluator(
                labelCol="top_6_label",
                rawPredictionCol="rawPrediction"
            )
            
            auc = evaluator.evaluate(predictions)
            
            # Calculate additional metrics
            multi_evaluator = MulticlassClassificationEvaluator(
                labelCol="top_6_label",
                predictionCol="prediction"
            )
            
            accuracy = multi_evaluator.evaluate(predictions, {multi_evaluator.metricName: "accuracy"})
            precision = multi_evaluator.evaluate(predictions, {multi_evaluator.metricName: "weightedPrecision"})
            recall = multi_evaluator.evaluate(predictions, {multi_evaluator.metricName: "weightedRecall"})
            
            # Log metrics
            mlflow.log_metric("auc", auc)
            mlflow.log_metric("accuracy", accuracy)
            mlflow.log_metric("precision", precision)
            mlflow.log_metric("recall", recall)
            
            logger.info(f"AUC: {auc:.4f}, Accuracy: {accuracy:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}")
            
            # Log model
            mlflow.spark.log_model(
                model,
                artifact_path="spark_rf_model",
                registered_model_name="pl_top6_model"
            )
            
            logger.info("Model registered with MLflow")
            return model, {"auc": auc, "accuracy": accuracy, "precision": precision, "recall": recall}

def main():
    pipeline = ModelTrainingPipeline(
        spark_master_url="spark://spark-master:7077",
        mlflow_uri="http://mlflow:5000"
    )
    
    # Read training data
    training_data = pipeline.read_training_data("/data/processed/training_data_delta")
    
    # Split data
    train_df, test_df = pipeline.split_data(training_data, train_ratio=0.8)
    
    # Feature columns
    feature_cols = [
        "avg_xg", "avg_goals", "total_assists", "squad_depth",
        "avg_pass_accuracy", "avg_tackles", "avg_interceptions",
        "xg_per_match", "goals_per_match", "avg_possession",
        "win_ratio", "points_per_match", "xg_momentum", "xg_difference",
        "defensive_rating"
    ]
    
    # Build and train pipeline
    ml_pipeline = pipeline.build_pipeline(feature_cols)
    model, metrics = pipeline.train_model(train_df, test_df, ml_pipeline)
    
    logger.info(f"Model training completed with metrics: {metrics}")

if __name__ == "__main__":
    main()
