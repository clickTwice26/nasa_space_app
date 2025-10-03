#!/usr/bin/env python3
"""
Precipitation Prediction Models
Multiple ML models for different weather prediction tasks
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, TimeSeriesSplit, GridSearchCV
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.neural_network import MLPRegressor
import joblib
from pathlib import Path
from typing import Dict, List, Tuple, Any
import warnings
warnings.filterwarnings('ignore')

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("XGBoost not available. Install with: pip install xgboost")

try:
    import lightgbm as lgb
    LIGHTGBM_AVAILABLE = True
except ImportError:
    LIGHTGBM_AVAILABLE = False
    print("LightGBM not available. Install with: pip install lightgbm")

class PrecipitationPredictor:
    """
    Machine Learning models for precipitation prediction
    Supports multiple prediction tasks:
    1. Next-day precipitation prediction
    2. Weekly precipitation forecast
    3. Precipitation intensity classification
    4. Drought risk assessment
    """
    
    def __init__(self, data_path: str = None):
        self.data_path = data_path
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.model_performance = {}
        
        # Model configurations
        self.model_configs = {
            'linear': LinearRegression(),
            'ridge': Ridge(alpha=1.0),
            'lasso': Lasso(alpha=0.1),
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boost': GradientBoostingRegressor(n_estimators=100, random_state=42),
            'neural_network': MLPRegressor(hidden_layer_sizes=(100, 50), max_iter=500, random_state=42),
            'svr': SVR(kernel='rbf', C=1.0, gamma='scale')
        }
        
        if XGBOOST_AVAILABLE:
            self.model_configs['xgboost'] = xgb.XGBRegressor(
                n_estimators=100, 
                learning_rate=0.1, 
                max_depth=6, 
                random_state=42
            )
        
        if LIGHTGBM_AVAILABLE:
            self.model_configs['lightgbm'] = lgb.LGBMRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=6,
                random_state=42,
                verbosity=-1
            )
    
    def load_data(self, filepath: str = None) -> pd.DataFrame:
        """Load preprocessed data"""
        if filepath is None:
            filepath = self.data_path
        
        df = pd.read_csv(filepath)
        df['date'] = pd.to_datetime(df['date'])
        return df
    
    def prepare_features(self, df: pd.DataFrame, target_column: str, 
                        feature_columns: List[str] = None) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Prepare features and target for ML models"""
        
        if feature_columns is None:
            # Automatically select numeric columns (excluding date and target)
            feature_columns = df.select_dtypes(include=[np.number]).columns.tolist()
            feature_columns = [col for col in feature_columns if col != target_column]
        
        # Remove any columns with all NaN values
        feature_columns = [col for col in feature_columns if col in df.columns and not df[col].isna().all()]
        
        X = df[feature_columns].values
        y = df[target_column].values
        
        # Remove rows with NaN values
        mask = ~(np.isnan(X).any(axis=1) | np.isnan(y))
        X = X[mask]
        y = y[mask]
        
        print(f"Features shape: {X.shape}")
        print(f"Target shape: {y.shape}")
        print(f"Feature columns: {feature_columns}")
        
        return X, y, feature_columns
    
    def create_precipitation_classes(self, precip_values: np.ndarray) -> np.ndarray:
        """Create precipitation intensity classes for classification"""
        # Define precipitation classes
        # 0: No rain (< 0.1mm)
        # 1: Light rain (0.1 - 2.5mm)
        # 2: Moderate rain (2.5 - 10mm)
        # 3: Heavy rain (10 - 50mm)
        # 4: Very heavy rain (> 50mm)
        
        classes = np.zeros_like(precip_values, dtype=int)
        classes[(precip_values >= 0.1) & (precip_values < 2.5)] = 1
        classes[(precip_values >= 2.5) & (precip_values < 10)] = 2
        classes[(precip_values >= 10) & (precip_values < 50)] = 3
        classes[precip_values >= 50] = 4
        
        return classes
    
    def train_model(self, X_train: np.ndarray, y_train: np.ndarray, 
                   model_name: str, scale_features: bool = True) -> Dict[str, Any]:
        """Train a single model"""
        
        if model_name not in self.model_configs:
            raise ValueError(f"Model {model_name} not available. Choose from: {list(self.model_configs.keys())}")
        
        print(f"Training {model_name}...")
        
        # Scale features if requested
        scaler = None
        if scale_features and model_name in ['neural_network', 'svr', 'linear', 'ridge', 'lasso']:
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
        else:
            X_train_scaled = X_train
        
        # Train model
        model = self.model_configs[model_name]
        model.fit(X_train_scaled, y_train)
        
        # Store model and scaler
        self.models[model_name] = model
        if scaler:
            self.scalers[model_name] = scaler
        
        # Get feature importance if available
        if hasattr(model, 'feature_importances_'):
            self.feature_importance[model_name] = model.feature_importances_
        elif hasattr(model, 'coef_'):
            self.feature_importance[model_name] = np.abs(model.coef_)
        
        return {'model': model, 'scaler': scaler}
    
    def evaluate_model(self, model_name: str, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, float]:
        """Evaluate a trained model"""
        
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not trained yet")
        
        model = self.models[model_name]
        
        # Scale features if scaler exists
        if model_name in self.scalers:
            X_test_scaled = self.scalers[model_name].transform(X_test)
        else:
            X_test_scaled = X_test
        
        # Make predictions
        y_pred = model.predict(X_test_scaled)
        
        # Calculate metrics
        metrics = {
            'mse': mean_squared_error(y_test, y_pred),
            'rmse': np.sqrt(mean_squared_error(y_test, y_pred)),
            'mae': mean_absolute_error(y_test, y_pred),
            'r2': r2_score(y_test, y_pred)
        }
        
        self.model_performance[model_name] = metrics
        
        return metrics
    
    def train_all_models(self, X_train: np.ndarray, y_train: np.ndarray, 
                        X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Dict[str, float]]:
        """Train and evaluate all available models"""
        
        print("Training all models...")
        results = {}
        
        for model_name in self.model_configs.keys():
            try:
                # Train model
                self.train_model(X_train, y_train, model_name)
                
                # Evaluate model
                metrics = self.evaluate_model(model_name, X_test, y_test)
                results[model_name] = metrics
                
                print(f"{model_name}: RMSE={metrics['rmse']:.4f}, R2={metrics['r2']:.4f}")
                
            except Exception as e:
                print(f"Error training {model_name}: {e}")
                continue
        
        return results
    
    def predict(self, model_name: str, X: np.ndarray) -> np.ndarray:
        """Make predictions with a trained model"""
        
        if model_name not in self.models:
            raise ValueError(f"Model {model_name} not trained yet")
        
        model = self.models[model_name]
        
        # Scale features if scaler exists
        if model_name in self.scalers:
            X_scaled = self.scalers[model_name].transform(X)
        else:
            X_scaled = X
        
        return model.predict(X_scaled)
    
    def get_best_model(self) -> str:
        """Get the name of the best performing model based on RMSE"""
        if not self.model_performance:
            raise ValueError("No models trained yet")
        
        best_model = min(self.model_performance.keys(), 
                        key=lambda x: self.model_performance[x]['rmse'])
        return best_model
    
    def save_models(self, save_dir: str):
        """Save all trained models"""
        save_path = Path(save_dir)
        save_path.mkdir(exist_ok=True)
        
        # Save models
        for model_name, model in self.models.items():
            model_file = save_path / f"{model_name}_model.joblib"
            joblib.dump(model, model_file)
        
        # Save scalers
        for model_name, scaler in self.scalers.items():
            scaler_file = save_path / f"{model_name}_scaler.joblib"
            joblib.dump(scaler, scaler_file)
        
        # Save performance metrics
        performance_file = save_path / "model_performance.joblib"
        joblib.dump(self.model_performance, performance_file)
        
        # Save feature importance
        importance_file = save_path / "feature_importance.joblib"
        joblib.dump(self.feature_importance, importance_file)
        
        print(f"Models saved to {save_path}")
    
    def load_models(self, load_dir: str):
        """Load saved models"""
        load_path = Path(load_dir)
        
        # Load models
        for model_file in load_path.glob("*_model.joblib"):
            model_name = model_file.stem.replace("_model", "")
            self.models[model_name] = joblib.load(model_file)
        
        # Load scalers
        for scaler_file in load_path.glob("*_scaler.joblib"):
            model_name = scaler_file.stem.replace("_scaler", "")
            self.scalers[model_name] = joblib.load(scaler_file)
        
        # Load performance metrics
        performance_file = load_path / "model_performance.joblib"
        if performance_file.exists():
            self.model_performance = joblib.load(performance_file)
        
        # Load feature importance
        importance_file = load_path / "feature_importance.joblib"
        if importance_file.exists():
            self.feature_importance = joblib.load(importance_file)
        
        print(f"Models loaded from {load_path}")

class WeatherAppPredictor:
    """
    Simplified prediction interface for weather app integration
    """
    
    def __init__(self, model_dir: str):
        self.predictor = PrecipitationPredictor()
        self.predictor.load_models(model_dir)
        self.feature_columns = None
    
    def predict_next_day_precipitation(self, current_weather_data: Dict) -> Dict:
        """
        Predict next day precipitation based on current weather data
        
        Args:
            current_weather_data: Dict with current weather features
            
        Returns:
            Dict with prediction results
        """
        try:
            # Convert input to feature array
            if self.feature_columns is None:
                # This should be loaded from model metadata
                raise ValueError("Feature columns not set. Load feature metadata.")
            
            # Create feature array from input data
            features = np.array([[current_weather_data.get(col, 0) for col in self.feature_columns]])
            
            # Get best model
            best_model = self.predictor.get_best_model()
            
            # Make prediction
            prediction = self.predictor.predict(best_model, features)[0]
            
            # Classify precipitation intensity
            if prediction < 0.1:
                intensity = "No rain"
                category = 0
            elif prediction < 2.5:
                intensity = "Light rain"
                category = 1
            elif prediction < 10:
                intensity = "Moderate rain"
                category = 2
            elif prediction < 50:
                intensity = "Heavy rain"
                category = 3
            else:
                intensity = "Very heavy rain"
                category = 4
            
            return {
                'predicted_precipitation_mm': round(prediction, 2),
                'intensity': intensity,
                'category': category,
                'confidence': self.predictor.model_performance[best_model]['r2'],
                'model_used': best_model
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'predicted_precipitation_mm': 0,
                'intensity': 'Unknown',
                'category': 0
            }
    
    def predict_weekly_trend(self, current_weather_data: Dict) -> List[Dict]:
        """
        Predict precipitation trend for the next 7 days
        """
        weekly_predictions = []
        
        for day in range(7):
            # This is a simplified approach - in reality, you'd need to update
            # features based on previous predictions
            prediction = self.predict_next_day_precipitation(current_weather_data)
            prediction['day'] = day + 1
            weekly_predictions.append(prediction)
        
        return weekly_predictions
    
    def assess_drought_risk(self, historical_data: List[float], days_ahead: int = 30) -> Dict:
        """
        Assess drought risk based on historical precipitation
        """
        recent_precip = np.array(historical_data[-30:])  # Last 30 days
        avg_daily_precip = np.mean(recent_precip)
        
        # Simple drought risk assessment
        if avg_daily_precip < 0.1:
            risk_level = "Very High"
            risk_score = 0.9
        elif avg_daily_precip < 0.5:
            risk_level = "High"
            risk_score = 0.7
        elif avg_daily_precip < 1.0:
            risk_level = "Moderate"
            risk_score = 0.5
        elif avg_daily_precip < 2.0:
            risk_level = "Low"
            risk_score = 0.3
        else:
            risk_level = "Very Low"
            risk_score = 0.1
        
        return {
            'drought_risk_level': risk_level,
            'risk_score': risk_score,
            'avg_daily_precipitation': round(avg_daily_precip, 2),
            'days_analyzed': len(recent_precip)
        }

def main():
    """Example usage"""
    # This would be run after data preprocessing
    print("Precipitation Prediction Models")
    print("===============================")
    print("This script provides ML models for precipitation prediction.")
    print("Run precipitation_analyzer.py first to create the dataset.")
    
    # Example of how to use the models:
    # 1. Load data
    # 2. Prepare features
    # 3. Train models
    # 4. Evaluate performance
    # 5. Save best models for weather app

if __name__ == "__main__":
    main()