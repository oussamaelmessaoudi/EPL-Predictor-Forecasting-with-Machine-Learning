from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, avg, sum as spark_sum, count, max as spark_max, min as spark_min,
    lag, lead, row_number, when, coalesce, lit
)
from pyspark.sql.window import Window
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FeatureEngineeringPipeline:
    def __init__(self, spark_master_url="local"):
        self.spark = SparkSession.builder \
            .appName("PLFeatureEngineering") \
            .master(spark_master_url) \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("INFO")

    def read_delta_table(self, path: str):
        """Read data from Delta Lake"""
        return self.spark.read.format("delta").load(path)

    def engineer_team_features(self, matches_df, players_df):
        """Engineer features at team level"""
        # Aggregate player statistics by team
        team_stats = players_df.groupBy("team_name", "season") \
            .agg(
                avg("xg_per_game").alias("avg_xg"),
                avg("goals_per_game").alias("avg_goals"),
                spark_sum("assists").alias("total_assists"),
                count("player_id").alias("squad_depth"),
                avg("pass_accuracy").alias("avg_pass_accuracy"),
                avg("tackles_per_game").alias("avg_tackles"),
                avg("interceptions_per_game").alias("avg_interceptions")
            )

        # Aggregate match statistics
        match_stats = matches_df.groupBy("team_name", "season") \
            .agg(
                avg("xg").alias("xg_per_match"),
                avg("goals").alias("goals_per_match"),
                avg("possession").alias("avg_possession"),
                count("match_id").alias("matches_played"),
                spark_sum(when(col("result") == "W", 1).otherwise(0)) \
                    .alias("wins"),
                spark_sum(when(col("result") == "D", 1).otherwise(0)) \
                    .alias("draws"),
                spark_sum(when(col("result") == "L", 1).otherwise(0)) \
                    .alias("losses")
            )

        # Calculate derived features
        match_stats = match_stats.withColumn(
            "win_ratio",
            col("wins") / col("matches_played")
        ).withColumn(
            "points_per_match",
            (col("wins") * 3 + col("draws")) / col("matches_played")
        )

        # Join team and match stats
        team_features = team_stats.join(
            match_stats,
            on=["team_name", "season"],
            how="left"
        )

        logger.info(f"Engineered features for {team_features.count()} team-seasons")
        return team_features

    def add_temporal_features(self, features_df):
        """Add rolling window and trend features"""
        window_spec = Window.partitionBy("team_name").orderBy("season")
        
        features_with_trends = features_df.withColumn(
            "prev_season_points",
            lag("points_per_match").over(window_spec)
        ).withColumn(
            "xg_momentum",
            col("xg_per_match") - coalesce(col("prev_season_points"), col("xg_per_match"))
        ).withColumn(
            "xg_difference",
            col("xg_per_match") - col("goals_per_match")
        ).withColumn(
            "defensive_rating",
            col("avg_tackles") + col("avg_interceptions")
        )
        
        return features_with_trends

    def add_target_variable(self, features_df, final_standings_df):
        """Add target variable: Top 6 or not"""
        features_with_target = features_df.join(
            final_standings_df.select(
                col("team_name"),
                col("season"),
                when(col("position") <= 6, 1).otherwise(0).alias("top_6_label")
            ),
            on=["team_name", "season"],
            how="left"
        )
        
        return features_with_target

    def prepare_training_data(self, features_df):
        """Prepare final training dataset"""
        # Handle missing values
        training_df = features_df.fillna({
            "avg_xg": 0,
            "avg_goals": 0,
            "total_assists": 0,
            "squad_depth": 11,
            "win_ratio": 0,
            "xg_difference": 0,
            "defensive_rating": 0
        })
        
        # Select feature columns
        feature_cols = [
            "avg_xg", "avg_goals", "total_assists", "squad_depth",
            "avg_pass_accuracy", "avg_tackles", "avg_interceptions",
            "xg_per_match", "goals_per_match", "avg_possession",
            "win_ratio", "points_per_match", "xg_momentum", "xg_difference",
            "defensive_rating", "top_6_label"
        ]
        
        training_data = training_df.select(feature_cols)
        
        logger.info(f"Prepared {training_data.count()} training samples")
        return training_data

def main():
    pipeline = FeatureEngineeringPipeline(spark_master_url="spark://spark-master:7077")
    
    # Read data from Delta Lake
    matches_df = pipeline.read_delta_table("/data/processed/matches_delta")
    players_df = pipeline.read_delta_table("/data/processed/players_delta")
    standings_df = pipeline.read_delta_table("/data/processed/standings_delta")
    
    # Engineer features
    team_features = pipeline.engineer_team_features(matches_df, players_df)
    features_with_trends = pipeline.add_temporal_features(team_features)
    features_with_target = pipeline.add_target_variable(features_with_trends, standings_df)
    training_data = pipeline.prepare_training_data(features_with_target)
    
    # Save processed data
    training_data.write \
        .format("delta") \
        .mode("overwrite") \
        .save("/data/processed/training_data_delta")
    
    logger.info("Feature engineering pipeline completed")

if __name__ == "__main__":
    main()
