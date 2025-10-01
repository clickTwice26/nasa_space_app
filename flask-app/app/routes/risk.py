"""
Risk Analysis API Routes

This blueprint provides endpoints for agricultural risk analysis,
combining multiple NASA satellite data sources to deliver actionable
insights for farmers and agricultural decision makers.
"""

from flask import Blueprint, jsonify, request
from app.services.risk_engine import crop_risk_analysis
import logging

logger = logging.getLogger(__name__)

risk_bp = Blueprint('risk', __name__)

@risk_bp.route('/risk-alerts')
def get_risk_alerts():
    """
    Get comprehensive crop risk analysis for specified location and period.
    
    Query Parameters:
    - lat (float): Latitude (-90 to 90)
    - lon (float): Longitude (-180 to 180)
    - crop (string): Crop type (rice, wheat, potato, jute, corn)
    - start (string): Start date in YYYYMMDD format
    - end (string): End date in YYYYMMDD format
    
    Returns:
    - JSON with risk analysis, alerts, and farmer-friendly recommendations
    
    Example:
    GET /api/risk-alerts?lat=23.7644&lon=90.3897&crop=rice&start=20240925&end=20241001
    
    Response:
    {
      "success": true,
      "crop": "Rice",
      "risk_level": "medium",
      "alerts": ["🌧️ Heavy rainfall warning: 45mm", "🌱 Monitor soil moisture levels"],
      "summary": "Moderate risks identified for rice during Sep 25-Oct 1. 2 concerns to monitor.",
      "recommendations": ["💧 Improve drainage systems", "📱 Monitor weather updates daily"]
    }
    """
    try:
        # Get required parameters
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        crop = request.args.get('crop')
        start = request.args.get('start')
        end = request.args.get('end')
        
        # Validate required parameters
        missing_params = []
        if not lat:
            missing_params.append('lat')
        if not lon:
            missing_params.append('lon')
        if not crop:
            missing_params.append('crop')
        if not start:
            missing_params.append('start')
        if not end:
            missing_params.append('end')
        
        if missing_params:
            return jsonify({
                'success': False,
                'error': f"Missing required parameters: {', '.join(missing_params)}",
                'alerts': ["⚠️ Invalid request parameters"],
                'summary': "Unable to analyze risk due to missing information",
                'required_params': {
                    'lat': 'Latitude (-90 to 90)',
                    'lon': 'Longitude (-180 to 180)',
                    'crop': 'Crop type (rice, wheat, potato, jute, corn)',
                    'start': 'Start date (YYYYMMDD)',
                    'end': 'End date (YYYYMMDD)'
                },
                'example': '/api/risk-alerts?lat=23.7644&lon=90.3897&crop=rice&start=20240925&end=20241001'
            }), 400
        
        # Convert coordinates to float
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid coordinate values. Latitude and longitude must be numeric.',
                'alerts': ["⚠️ Invalid location coordinates"],
                'summary': "Unable to analyze risk due to invalid coordinates"
            }), 400
        
        # Validate crop type
        valid_crops = ['rice', 'wheat', 'potato', 'jute', 'corn']
        if crop.lower() not in valid_crops:
            return jsonify({
                'success': False,
                'error': f"Invalid crop type. Must be one of: {', '.join(valid_crops)}",
                'alerts': [f"⚠️ Unsupported crop: {crop}"],
                'summary': f"Risk analysis not available for {crop}",
                'supported_crops': valid_crops
            }), 400
        
        # Log the request
        logger.info(f"Risk analysis request: lat={lat}, lon={lon}, crop={crop}, start={start}, end={end}")
        
        # Perform risk analysis
        result = crop_risk_analysis(lat, lon, crop, start, end)
        
        # Handle analysis failure
        if not result.get('success'):
            logger.error(f"Risk analysis failed: {result.get('error', 'Unknown error')}")
            return jsonify({
                'success': False,
                'error': result.get('error', 'Unable to fetch data'),
                'crop': crop.title(),
                'alerts': ["⚠️ Risk analysis temporarily unavailable"],
                'summary': "Unable to complete risk analysis at this time. Please try again later.",
                'recommendations': ["📱 Check back in a few minutes", "🤝 Contact support if problem persists"]
            }), 500
        
        # Return successful analysis
        response = {
            'success': True,
            'crop': result.get('crop', crop.title()),
            'location': result.get('location', {'latitude': lat, 'longitude': lon}),
            'period': result.get('period', {'start': start, 'end': end}),
            'risk_level': result.get('risk_level', 'unknown'),
            'alerts': result.get('alerts', []),
            'summary': result.get('summary', 'Risk analysis completed'),
            'recommendations': result.get('recommendations', []),
            'data_availability': result.get('data_sources', {}),
            'analysis_timestamp': result.get('timestamp', 'unknown')
        }
        
        # Add mobile-friendly metadata
        response['mobile_friendly'] = {
            'emoji_alerts': len([alert for alert in response['alerts'] if any(emoji in alert for emoji in ['🌧️', '🌡️', '🟠', '✅', '⚠️', '🌊', '🏜️', '🔥', '❄️'])]),
            'total_alerts': len(response['alerts']),
            'has_recommendations': len(response['recommendations']) > 0,
            'status_color': {
                'low': '#28a745',      # Green
                'medium': '#ffc107',   # Yellow
                'high': '#dc3545'      # Red
            }.get(response['risk_level'], '#6c757d')  # Gray for unknown
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Unexpected error in risk-alerts endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred while analyzing crop risks.',
            'crop': request.args.get('crop', 'Unknown').title(),
            'alerts': ["⚠️ Service temporarily unavailable"],
            'summary': "Risk analysis service is experiencing issues. Please try again shortly.",
            'recommendations': ["📱 Try again in a few minutes", "🤝 Contact support if problem continues"]
        }), 500

@risk_bp.route('/risk-info')
def get_risk_info():
    """
    Get information about the risk analysis service and supported crops.
    
    Returns:
    - JSON with service information, supported crops, and usage examples
    """
    try:
        return jsonify({
            'success': True,
            'service': 'Agricultural Risk Analysis',
            'description': 'Intelligent crop risk analysis combining NASA satellite data',
            'supported_crops': [
                {
                    'name': 'Rice',
                    'code': 'rice',
                    'optimal_temp': '20-30°C',
                    'water_needs': 'High',
                    'common_risks': ['Flooding', 'Heat stress', 'Drought']
                },
                {
                    'name': 'Wheat',
                    'code': 'wheat',
                    'optimal_temp': '15-25°C',
                    'water_needs': 'Moderate',
                    'common_risks': ['Heat stress', 'Cold stress', 'Drought']
                },
                {
                    'name': 'Potato',
                    'code': 'potato',
                    'optimal_temp': '15-24°C',
                    'water_needs': 'Moderate',
                    'common_risks': ['Heat stress', 'Excess moisture', 'Frost']
                },
                {
                    'name': 'Jute',
                    'code': 'jute',
                    'optimal_temp': '24-35°C',
                    'water_needs': 'High',
                    'common_risks': ['Flooding', 'Drought', 'Cold stress']
                },
                {
                    'name': 'Corn',
                    'code': 'corn',
                    'optimal_temp': '20-30°C',
                    'water_needs': 'Moderate',
                    'common_risks': ['Heat stress', 'Drought', 'Cold stress']
                }
            ],
            'data_sources': [
                'NASA POWER API (Weather data)',
                'NASA GPM IMERG (Precipitation data)',
                'NASA MODIS (Vegetation health)',
                'FAO/World Bank (Historical trends)'
            ],
            'risk_levels': {
                'low': {
                    'color': '#28a745',
                    'description': 'Minimal risks, favorable conditions',
                    'emoji': '✅'
                },
                'medium': {
                    'color': '#ffc107',
                    'description': 'Some concerns to monitor',
                    'emoji': '⚠️'
                },
                'high': {
                    'color': '#dc3545',
                    'description': 'Critical risks requiring immediate attention',
                    'emoji': '🚨'
                }
            },
            'usage_example': {
                'endpoint': '/api/risk-alerts',
                'method': 'GET',
                'parameters': {
                    'lat': '23.7644',
                    'lon': '90.3897',
                    'crop': 'rice',
                    'start': '20240925',
                    'end': '20241001'
                },
                'example_url': '/api/risk-alerts?lat=23.7644&lon=90.3897&crop=rice&start=20240925&end=20241001'
            },
            'mobile_optimization': {
                'emoji_alerts': 'Alerts include emojis for quick recognition',
                'farmer_friendly': 'Simple language and actionable recommendations',
                'responsive_design': 'Optimized for mobile field use'
            }
        })
        
    except Exception as e:
        logger.error(f"Error in risk-info endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve service information'
        }), 500

@risk_bp.route('/risk-test')
def test_risk_service():
    """
    Test endpoint for quick service validation.
    
    Returns:
    - Sample risk analysis for demonstration purposes
    """
    try:
        # Use default test parameters for Dhaka, Bangladesh
        sample_result = crop_risk_analysis(
            lat=23.7644,
            lon=90.3897,
            crop='rice',
            start='20240925',
            end='20241001'
        )
        
        return jsonify({
            'success': True,
            'test_location': 'Dhaka, Bangladesh',
            'test_crop': 'Rice',
            'test_period': 'Sep 25 - Oct 1, 2024',
            'sample_result': sample_result,
            'service_status': 'operational' if sample_result.get('success') else 'degraded'
        })
        
    except Exception as e:
        logger.error(f"Error in risk-test endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Risk service test failed',
            'service_status': 'unavailable'
        }), 500