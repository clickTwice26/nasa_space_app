#!/usr/bin/env python3
"""
TerraPulse ML Routes
API endpoints for machine learning functionality integration
"""

from flask import Blueprint, jsonify, request, session, render_template
from app.services.ml.precipitation_predictor import precipitation_model
from app.services.ml.weather_analytics import weather_analytics
from app.services.ml.data_processor import data_processor, LocationData
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

ml_routes = Blueprint('ml_routes', __name__)

@ml_routes.route('/api/ml/precipitation/predict', methods=['POST'])
def predict_precipitation():
    """
    Predict precipitation based on current weather conditions
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        # Extract weather features
        features = {
            'temperature': data.get('temperature', 25.0),
            'humidity': data.get('humidity', 65.0),
            'pressure': data.get('pressure', 1013.0),
            'wind_speed': data.get('wind_speed', 10.0),
            'cloud_cover': data.get('cloud_cover', 50.0)
        }
        
        # Get prediction from ML model
        prediction = precipitation_model.predict_precipitation(features)
        
        return jsonify(prediction)
        
    except Exception as e:
        logger.error(f"Error in precipitation prediction: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@ml_routes.route('/api/ml/precipitation/forecast', methods=['POST'])
def get_precipitation_forecast():
    """
    Get 7-day precipitation forecast
    """
    try:
        data = request.get_json()
        
        # Base weather conditions
        base_features = {
            'temperature': data.get('temperature', 25.0),
            'humidity': data.get('humidity', 65.0),
            'pressure': data.get('pressure', 1013.0),
            'wind_speed': data.get('wind_speed', 10.0),
            'cloud_cover': data.get('cloud_cover', 50.0)
        }
        
        # Get weekly forecast
        forecast = precipitation_model.predict_weekly_forecast(base_features)
        
        return jsonify(forecast)
        
    except Exception as e:
        logger.error(f"Error in precipitation forecast: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@ml_routes.route('/api/ml/weather/trends', methods=['POST'])
def analyze_weather_trends():
    """
    Analyze weather trends from historical data
    """
    try:
        data = request.get_json()
        historical_data = data.get('historical_data', [])
        
        # If no historical data provided, generate sample data
        if not historical_data:
            # Generate sample historical data for demo
            historical_data = []
            for i in range(30):  # 30 days of data
                date = datetime.now() - timedelta(days=30-i)
                sample_data = {
                    'date': date.isoformat(),
                    'temperature': 25 + np.random.normal(0, 5),
                    'humidity': 65 + np.random.normal(0, 15),
                    'rainfall': max(0, np.random.exponential(3)),
                    'pressure': 1013 + np.random.normal(0, 10)
                }
                historical_data.append(sample_data)
        
        # Analyze trends
        trends = weather_analytics.analyze_weather_trends(historical_data)
        
        return jsonify(trends)
        
    except Exception as e:
        logger.error(f"Error analyzing weather trends: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@ml_routes.route('/api/ml/agriculture/insights', methods=['POST'])
def get_agricultural_insights():
    """
    Generate agricultural insights based on weather conditions
    """
    try:
        data = request.get_json()
        
        weather_data = {
            'temperature': data.get('temperature', 25.0),
            'humidity': data.get('humidity', 65.0),
            'rainfall': data.get('rainfall', 5.0),
            'pressure': data.get('pressure', 1013.0),
            'wind_speed': data.get('wind_speed', 10.0)
        }
        
        location_info = data.get('location', {})
        
        # Generate insights
        insights = weather_analytics.generate_agricultural_insights(weather_data, location_info)
        
        return jsonify(insights)
        
    except Exception as e:
        logger.error(f"Error generating agricultural insights: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@ml_routes.route('/api/ml/irrigation/analysis', methods=['POST'])
def analyze_irrigation_needs():
    """
    Analyze irrigation requirements based on weather and crop conditions
    """
    try:
        data = request.get_json()
        
        weather_data = {
            'temperature': data.get('temperature', 25.0),
            'humidity': data.get('humidity', 65.0),
            'rainfall': data.get('rainfall', 5.0),
            'wind_speed': data.get('wind_speed', 10.0)
        }
        
        crop_type = data.get('crop_type', 'rice')
        growth_stage = data.get('growth_stage', 'vegetative')
        
        # Analyze irrigation needs
        analysis = weather_analytics.analyze_irrigation_needs(
            weather_data, crop_type, growth_stage
        )
        
        return jsonify(analysis)
        
    except Exception as e:
        logger.error(f"Error analyzing irrigation needs: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@ml_routes.route('/api/ml/pest-disease/risk', methods=['POST'])
def predict_pest_disease_risk():
    """
    Predict pest and disease risks based on weather conditions
    """
    try:
        data = request.get_json()
        
        weather_data = {
            'temperature': data.get('temperature', 25.0),
            'humidity': data.get('humidity', 65.0),
            'rainfall': data.get('rainfall', 5.0)
        }
        
        # Predict risks
        risk_assessment = weather_analytics.predict_pest_disease_risk(weather_data)
        
        return jsonify(risk_assessment)
        
    except Exception as e:
        logger.error(f"Error predicting pest/disease risk: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@ml_routes.route('/api/ml/data/nasa-weather', methods=['POST'])
def fetch_nasa_weather():
    """
    Fetch weather data from NASA APIs
    """
    try:
        data = request.get_json()
        
        # Extract location data
        location = LocationData(
            latitude=data.get('latitude', 20.0),
            longitude=data.get('longitude', 77.0),
            elevation=data.get('elevation'),
            region=data.get('region'),
            climate_zone=data.get('climate_zone')
        )
        
        # Date range
        start_date = None
        end_date = None
        
        if data.get('start_date'):
            start_date = datetime.fromisoformat(data['start_date'].replace('Z', '+00:00'))
        if data.get('end_date'):
            end_date = datetime.fromisoformat(data['end_date'].replace('Z', '+00:00'))
        
        # Fetch NASA weather data
        nasa_data = data_processor.fetch_nasa_weather_data(location, start_date, end_date)
        
        return jsonify(nasa_data)
        
    except Exception as e:
        logger.error(f"Error fetching NASA weather data: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

@ml_routes.route('/api/ml/features/extract', methods=['POST'])
def extract_weather_features():
    """
    Extract ML features from weather data
    """
    try:
        data = request.get_json()
        
        # Create location object
        location_data = data.get('location', {})
        location = LocationData(
            latitude=location_data.get('latitude', 20.0),
            longitude=location_data.get('longitude', 77.0),
            elevation=location_data.get('elevation')
        )
        
        # Fetch NASA weather data for the location
        nasa_data = data_processor.fetch_nasa_weather_data(location)
        
        if not nasa_data.get('success'):
            return jsonify({
                'success': False,
                'error': 'Failed to fetch weather data'
            }), 400
        
        # Process weather observations
        observations = data_processor.process_weather_observations(nasa_data)
        
        if not observations:
            return jsonify({
                'success': False,
                'error': 'No weather observations processed'
            }), 400
        
        # Extract features
        features_df = data_processor.extract_features(observations, location)
        
        if features_df.empty:
            return jsonify({
                'success': False,
                'error': 'No features extracted'
            }), 400
        
        # Convert to dictionary for API response
        feature_dict = data_processor.aggregate_to_features_dict(features_df)
        
        return jsonify({
            'success': True,
            'features': feature_dict,
            'feature_count': len(feature_dict),
            'observation_count': len(observations),
            'location': location_data,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        })
        
    except Exception as e:
        logger.error(f"Error extracting weather features: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

# ML Dashboard Routes
@ml_routes.route('/ml-dashboard')
def ml_dashboard():
    """
    Render ML dashboard page
    """
    try:
        # Get user session data
        user_data = session.get('user_data', {})
        
        return render_template('ml_dashboard.html', user=user_data)
        
    except Exception as e:
        logger.error(f"Error rendering ML dashboard: {str(e)}")
        return render_template('error.html', error="Failed to load ML dashboard"), 500

@ml_routes.route('/precipitation-analysis')
def precipitation_analysis():
    """
    Render precipitation analysis page
    """
    try:
        user_data = session.get('user_data', {})
        
        return render_template('precipitation_analysis.html', user=user_data)
        
    except Exception as e:
        logger.error(f"Error rendering precipitation analysis: {str(e)}")
        return render_template('error.html', error="Failed to load precipitation analysis"), 500

@ml_routes.route('/agricultural-insights')
def agricultural_insights_page():
    """
    Render agricultural insights page
    """
    try:
        user_data = session.get('user_data', {})
        
        return render_template('agricultural_insights.html', user=user_data)
        
    except Exception as e:
        logger.error(f"Error rendering agricultural insights: {str(e)}")
        return render_template('error.html', error="Failed to load agricultural insights"), 500

# Import numpy for the trends endpoint
import numpy as np