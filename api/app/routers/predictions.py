from fastapi import APIRouter, Query, BackgroundTasks, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import mlflow.pyfunc
import pandas as pd
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class PredictionRequest(BaseModel):
    team_name: str
    avg_xg: float
    avg_goals: float
    total_assists: int
    squad_depth: int
    win_ratio: float
    xg_difference: float
    defensive_rating: float

class PredictionResponse(BaseModel):
    team: str
    prediction: str
    probability: float
    confidence: str

# Load model at startup
model = None

@router.on_event("startup")
async def load_model():
    global model
    try:
        model = mlflow.pyfunc.load_model("models:/pl_top6_model/production")
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")

@router.post("/predict/top6", response_model=PredictionResponse)
async def predict_top6(request: PredictionRequest):
    """Predict if a team will finish in top 6"""
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Prepare data
        data = pd.DataFrame([{
            "avg_xg": request.avg_xg,
            "avg_goals": request.avg_goals,
            "total_assists": request.total_assists,
            "squad_depth": request.squad_depth,
            "win_ratio": request.win_ratio,
            "xg_difference": request.xg_difference,
            "defensive_rating": request.defensive_rating,
        }])
        
        # Make prediction
        prediction = model.predict(data)
        probability = model.predict_proba(data)[0][1] if hasattr(model, 'predict_proba') else 0.5
        
        return PredictionResponse(
            team=request.team_name,
            prediction="Top 6" if prediction[0] == 1 else "Not Top 6",
            probability=float(probability),
            confidence=f"{probability * 100:.1f}%"
        )
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/current-season")
async def get_current_predictions(top_n: int = Query(6, ge=1, le=20)):
    """Get Top N team predictions for current season"""
    # TODO: Implement fetching from database/cache
    return {
        "season": "2024/25",
        "predictions": []
    }

@router.get("/team/{team_name}")
async def get_team_prediction(team_name: str):
    """Get specific team prediction with detailed metrics"""
    # TODO: Implement
    return {
        "team": team_name,
        "prediction": "Top 6",
        "probability": 0.75
    }

@router.post("/trigger-training")
async def trigger_model_training(background_tasks: BackgroundTasks):
    """Trigger model retraining pipeline"""
    background_tasks.add_task(retrain_model_pipeline)
    return {"status": "Training job submitted"}

def retrain_model_pipeline():
    """Background task for model retraining"""
    logger.info("Starting model retraining...")
    # TODO: Implement Spark job submission

@router.get("/historical/{season}")
async def get_historical_predictions(season: str):
    """Get predictions for a past season"""
    # TODO: Implement
    return {
        "season": season,
        "predictions": []
    }
