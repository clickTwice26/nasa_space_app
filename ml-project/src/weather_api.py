#!/usr/bin/env python3
"""
Weather Prediction API
FastAPI-based web service for precipitation prediction
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Optional
import numpy as np
import pandas as pd
import joblib
from pathlib import Path
from datetime import datetime, timedelta
import uvicorn

# Initialize FastAPI app
app = FastAPI(
    title="Precipitation Prediction API",
    description="Machine Learning-based precipitation forecasting for weather applications",
    version="1.0.0"
)

# Global variables for loaded models
models = {}
scalers = {}
feature_columns = []
class_names = []

class WeatherInput(BaseModel):
    """Input model for weather prediction"""
    latitude: float
    longitude: float
    date: str
    temperature: Optional[float] = 20.0
    humidity: Optional[float] = 50.0
    pressure: Optional[float] = 1013.25
    wind_speed: Optional[float] = 10.0
    previous_precipitation: Optional[List[float]] = [0.0, 0.0, 0.0]  # Last 3 days

class PredictionResponse(BaseModel):
    """Response model for predictions"""
    location: Dict[str, float]
    date: str
    precipitation_forecast: Dict
    alerts: Dict
    model_info: Dict

@app.on_event("startup")
async def load_models():
    """Load ML models on startup"""
    global models, scalers, feature_columns, class_names
    
    model_dir = Path("models")
    if not model_dir.exists():
        print("Warning: Models directory not found. Please train models first.")
        return
    
    try:
        # Load models
        for model_file in model_dir.glob("*_model.joblib"):
            model_name = model_file.stem.replace("_model", "")
            models[model_name] = joblib.load(model_file)
        
        # Load scalers
        for scaler_file in model_dir.glob("*_scaler.joblib"):
            model_name = scaler_file.stem.replace("_scaler", "")
            scalers[model_name] = joblib.load(scaler_file)
        
        # Load metadata
        if (model_dir / "feature_columns.joblib").exists():
            feature_columns = joblib.load(model_dir / "feature_columns.joblib")
        
        if (model_dir / "class_names.joblib").exists():
            class_names = joblib.load(model_dir / "class_names.joblib")
        
        print(f"Loaded {len(models)} models successfully")
        
    except Exception as e:
        print(f"Error loading models: {e}")

def create_features_from_input(weather_input: WeatherInput) -> np.ndarray:
    """Convert weather input to feature array"""
    # This is a simplified feature creation
    # In practice, you'd need to map input to your trained features
    
    # Extract date features
    date_obj = datetime.strptime(weather_input.date, "%Y-%m-%d")
    
    # Basic features (simplified for demo)
    features = [
        weather_input.latitude,
        weather_input.longitude,
        weather_input.temperature,
        weather_input.humidity,
        weather_input.pressure,
        weather_input.wind_speed,
        date_obj.month,
        date_obj.day,
        date_obj.timetuple().tm_yday,
        np.sin(2 * np.pi * date_obj.month / 12),
        np.cos(2 * np.pi * date_obj.month / 12),
    ]
    
    # Add previous precipitation values
    features.extend(weather_input.previous_precipitation)
    
    # Pad or truncate to match expected feature count
    if len(feature_columns) > 0:
        while len(features) < len(feature_columns):
            features.append(0.0)
        features = features[:len(feature_columns)]
    
    return np.array([features])

def get_best_model_name() -> str:
    """Get the best performing model name"""
    # For now, prefer random_forest, then gradient_boost, then others
    preferred_order = ['random_forest', 'gradient_boost', 'xgboost', 'lightgbm']
    
    for model_name in preferred_order:
        if model_name in models:
            return model_name
    
    # Return first available model
    if models:
        return list(models.keys())[0]
    
    raise ValueError("No models available")

@app.get("/")
async def root():
    """API status endpoint"""
    return {
        "message": "Precipitation Prediction API",
        "status": "running",
        "models_loaded": len(models),
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "models_available": list(models.keys()),
        "features_count": len(feature_columns)
    }

@app.post("/predict", response_model=PredictionResponse)
async def predict_precipitation(weather_input: WeatherInput):
    """Predict precipitation for given weather conditions"""
    
    if not models:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    try:
        # Get best model
        best_model_name = get_best_model_name()
        model = models[best_model_name]
        
        # Create features
        features = create_features_from_input(weather_input)
        
        # Scale features if scaler available
        if best_model_name in scalers:
            features = scalers[best_model_name].transform(features)
        
        # Make prediction
        prediction = model.predict(features)[0]
        
        # Classify intensity
        if prediction < 0.1:
            intensity = "No rain"
            category = 0
            probability = 5
        elif prediction < 2.5:
            intensity = "Light rain"
            category = 1
            probability = 25
        elif prediction < 10:
            intensity = "Moderate rain"
            category = 2
            probability = 50
        elif prediction < 50:
            intensity = "Heavy rain"
            category = 3
            probability = 75
        else:
            intensity = "Very heavy rain"
            category = 4
            probability = 90
        
        # Determine alerts
        flood_risk = "high" if category >= 3 else "moderate" if category >= 2 else "low"
        drought_risk = "high" if category == 0 else "moderate" if category == 1 else "low"
        
        # Create response
        response = PredictionResponse(
            location={
                "latitude": weather_input.latitude,
                "longitude": weather_input.longitude
            },
            date=weather_input.date,
            precipitation_forecast={
                "amount_mm": round(max(prediction, 0), 2),
                "intensity": intensity,
                "category": category,
                "probability": probability
            },
            alerts={
                "flood_risk": flood_risk,
                "drought_risk": drought_risk
            },
            model_info={
                "model_type": best_model_name,
                "confidence_score": 0.8  # Placeholder
            }
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/predict/weekly")
async def predict_weekly(weather_input: WeatherInput):
    """Predict precipitation for the next 7 days"""
    
    if not models:
        raise HTTPException(status_code=503, detail="Models not loaded")
    
    try:
        weekly_predictions = []
        
        # Generate predictions for next 7 days
        base_date = datetime.strptime(weather_input.date, "%Y-%m-%d")
        
        for i in range(7):
            pred_date = base_date + timedelta(days=i)
            
            # Create modified input for each day
            daily_input = weather_input.copy()
            daily_input.date = pred_date.strftime("%Y-%m-%d")
            
            # Get prediction
            prediction = await predict_precipitation(daily_input)
            prediction_dict = prediction.dict()
            prediction_dict["day"] = i + 1
            
            weekly_predictions.append(prediction_dict)
        
        return {
            "location": {
                "latitude": weather_input.latitude,
                "longitude": weather_input.longitude
            },
            "forecast_period": f"{weather_input.date} to {(base_date + timedelta(days=6)).strftime('%Y-%m-%d')}",
            "daily_forecasts": weekly_predictions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Weekly prediction error: {str(e)}")

@app.get("/models/info")
async def get_model_info():
    """Get information about loaded models"""
    return {
        "available_models": list(models.keys()),
        "feature_count": len(feature_columns),
        "feature_columns": feature_columns[:10] if feature_columns else [],  # First 10 for brevity
        "precipitation_classes": class_names if class_names else []
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)