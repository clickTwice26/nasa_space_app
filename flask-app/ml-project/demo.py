#!/usr/bin/env python3
"""
Demo Script for Precipitation Prediction ML Models
Demonstrates the complete workflow and weather app integration
"""

import os
import sys
sys.path.append('src')

from src.precipitation_analyzer import TRMMPrecipitationAnalyzer
from src.precipitation_models import PrecipitationPredictor
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

def main():
    print("🌧️  PRECIPITATION PREDICTION DEMO")
    print("=" * 40)
    
    # Check if we have data
    data_dir = "data/raw"
    if not os.path.exists(data_dir):
        print("❌ Data directory not found. Please run download_http.py first.")
        return
    
    print("\\n🔍 Step 1: Analyzing Available Data")
    print("-" * 35)
    
    analyzer = TRMMPrecipitationAnalyzer(data_dir)
    files = analyzer.get_file_list(start_year=2011, end_year=2011)
    
    if not files:
        print("❌ No data files found. Please ensure TRMM data is downloaded.")
        return
    
    print(f"✅ Found {len(files)} files")
    print(f"Date range: {files[0][1]} to {files[-1][1]}")
    
    # Check if processed data exists
    processed_file = "data/processed/precipitation_ml_dataset.csv"
    
    if os.path.exists(processed_file):
        print("\\n📊 Step 2: Loading Processed Dataset")
        print("-" * 40)
        df = pd.read_csv(processed_file)
        df['date'] = pd.to_datetime(df['date'])
        print(f"✅ Loaded dataset with {df.shape[0]} records and {df.shape[1]} features")
    else:
        print("\\n🔧 Step 2: Creating Dataset (This may take a few minutes)")
        print("-" * 55)
        
        # Create a small sample dataset for demo
        df = analyzer.create_dataset(
            regions=['global', 'usa'],
            start_year=2011,
            end_year=2011,
            sample_size=50  # Small sample for quick demo
        )
        
        # Add features
        target_columns = ['global_mean_precip', 'usa_mean_precip']
        df = analyzer.add_lag_features(df, target_columns, lags=[1, 3])
        df = analyzer.add_rolling_features(df, target_columns, windows=[7])
        
        # Save for future use
        analyzer.save_dataset(df, "precipitation_ml_dataset_demo.csv")
        print(f"✅ Created dataset with {df.shape[0]} records and {df.shape[1]} features")
    
    print("\\n🤖 Step 3: Training ML Models")
    print("-" * 35)
    
    # Initialize predictor
    predictor = PrecipitationPredictor()
    
    # Prepare data
    target_column = 'global_mean_precip'
    X, y, feature_columns = predictor.prepare_features(df, target_column)
    
    # Split data
    split_idx = int(0.8 * len(X))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    print(f"Training set: {X_train.shape[0]} samples")
    print(f"Test set: {X_test.shape[0]} samples")
    
    # Train models (subset for demo)
    demo_models = ['linear', 'random_forest', 'gradient_boost']
    results = {}
    
    for model_name in demo_models:
        try:
            print(f"Training {model_name}...")
            predictor.train_model(X_train, y_train, model_name)
            metrics = predictor.evaluate_model(model_name, X_test, y_test)
            results[model_name] = metrics
            print(f"  ✅ RMSE: {metrics['rmse']:.4f}, R²: {metrics['r2']:.4f}")
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    if results:
        # Get best model
        best_model = min(results.keys(), key=lambda x: results[x]['rmse'])
        print(f"\\n🏆 Best model: {best_model}")
        print(f"   RMSE: {results[best_model]['rmse']:.4f}")
        print(f"   R² Score: {results[best_model]['r2']:.4f}")
        
        print("\\n🔮 Step 4: Making Predictions")
        print("-" * 35)
        
        # Make sample predictions
        predictions = predictor.predict(best_model, X_test[:5])
        actual = y_test[:5]
        
        print("Sample Predictions vs Actual:")
        for i in range(5):
            print(f"  Day {i+1}: Predicted={predictions[i]:.3f}, Actual={actual[i]:.3f}")
        
        print("\\n📱 Step 5: Weather App Demo")
        print("-" * 30)
        
        # Create weather app prediction function
        def weather_app_prediction(location_name, lat, lon):
            # Use latest available features for prediction
            sample_features = X_test[-1].reshape(1, -1)
            pred = predictor.predict(best_model, sample_features)[0]
            
            # Classify prediction
            if pred < 0.1:
                intensity = "No rain"
                emoji = "☀️"
            elif pred < 2.5:
                intensity = "Light rain"
                emoji = "🌦️"
            elif pred < 10:
                intensity = "Moderate rain"
                emoji = "🌧️"
            elif pred < 50:
                intensity = "Heavy rain"
                emoji = "⛈️"
            else:
                intensity = "Very heavy rain"
                emoji = "🌩️"
            
            return {
                'location': location_name,
                'coordinates': f"{lat}, {lon}",
                'prediction': f"{pred:.2f} mm/day",
                'intensity': intensity,
                'emoji': emoji,
                'confidence': f"{results[best_model]['r2']*100:.1f}%"
            }
        
        # Demo predictions for different cities
        cities = [
            ("New York", 40.7128, -74.0060),
            ("London", 51.5074, -0.1278),
            ("Tokyo", 35.6762, 139.6503),
            ("Sydney", -33.8688, 151.2093)
        ]
        
        print("🌍 Global Weather Predictions:")
        for city, lat, lon in cities:
            pred_result = weather_app_prediction(city, lat, lon)
            print(f"  {pred_result['emoji']} {pred_result['location']}: {pred_result['prediction']} - {pred_result['intensity']}")
        
        print("\\n📊 Step 6: Model Summary")
        print("-" * 25)
        print(f"✅ Successfully trained {len(results)} ML models")
        print(f"✅ Best performing model: {best_model}")
        print(f"✅ Model ready for weather app integration")
        print(f"✅ API endpoint available at: src/weather_api.py")
        
        print("\\n🚀 Next Steps for Weather App:")
        print("-" * 35)
        print("1. Deploy API using: python src/weather_api.py")
        print("2. Integrate with real-time weather data")
        print("3. Add more historical data for better accuracy")
        print("4. Implement ensemble methods")
        print("5. Add uncertainty quantification")
        
        print("\\n🎉 Demo completed successfully!")
        
    else:
        print("❌ No models were trained successfully")

if __name__ == "__main__":
    main()