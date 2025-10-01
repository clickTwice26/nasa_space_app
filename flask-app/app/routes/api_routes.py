from flask import Blueprint, jsonify, request
from app.services.data_service import DataService
from app.services.power_api import PowerAPIService
from app.services.gpm_api import get_gpm_data
from app.services.modis_api import get_modis_air_quality
from app.services.worldview_api import get_worldview_image, get_available_layers
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint('api', __name__)

@api_bp.route('/data')
def get_data():
    """Get general data endpoint"""
    try:
        data_service = DataService()
        result = data_service.get_sample_data()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error in data endpoint: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@api_bp.route('/power-data')
def get_power_data():
    """
    Get NASA POWER satellite weather data for specified location and date range.
    
    Query Parameters:
    - lat (float): Latitude (-90 to 90)
    - lon (float): Longitude (-180 to 180)
    - start (string): Start date in YYYYMMDD format
    - end (string): End date in YYYYMMDD format
    - parameters (string, optional): Comma-separated list of parameters (default: T2M,PRECTOTCORR)
    
    Returns:
    - JSON with weather data including temperature, precipitation, and metadata
    """
    try:
        # Get required parameters
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        start = request.args.get('start')
        end = request.args.get('end')
        parameters = request.args.get('parameters', 'T2M,PRECTOTCORR')
        
        # Validate required parameters
        missing_params = []
        if not lat:
            missing_params.append('lat')
        if not lon:
            missing_params.append('lon')
        if not start:
            missing_params.append('start')
        if not end:
            missing_params.append('end')
        
        if missing_params:
            return jsonify({
                'success': False,
                'error': f"Missing required parameters: {', '.join(missing_params)}",
                'data': [],
                'required_params': {
                    'lat': 'Latitude (-90 to 90)',
                    'lon': 'Longitude (-180 to 180)',
                    'start': 'Start date (YYYYMMDD)',
                    'end': 'End date (YYYYMMDD)',
                    'parameters': 'Comma-separated parameters (optional)'
                }
            }), 400
        
        # Convert coordinates to float
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid coordinate values. Latitude and longitude must be numeric.',
                'data': []
            }), 400
        
        # Log the request
        logger.info(f"NASA POWER API request: lat={lat}, lon={lon}, start={start}, end={end}, params={parameters}")
        
        # Initialize the PowerAPIService and get data
        power_service = PowerAPIService()
        result = power_service.get_power_data(lat, lon, start, end, parameters)
        
        # Return appropriate HTTP status code
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Unexpected error in power-data endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred while processing your request.',
            'data': []
        }), 500

@api_bp.route('/gpm-data')
def get_gpm_precipitation_data():
    """
    Get NASA GPM IMERG precipitation data for specified location and date range.
    
    Query Parameters:
    - lat (float): Latitude (-90 to 90)
    - lon (float): Longitude (-180 to 180)
    - start (string): Start date in YYYYMMDD format
    - end (string): End date in YYYYMMDD format
    
    Returns:
    - JSON with precipitation data and metadata
    """
    try:
        # Get required parameters
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        start = request.args.get('start')
        end = request.args.get('end')
        
        # Validate required parameters
        missing_params = []
        if not lat:
            missing_params.append('lat')
        if not lon:
            missing_params.append('lon')
        if not start:
            missing_params.append('start')
        if not end:
            missing_params.append('end')
        
        if missing_params:
            return jsonify({
                'success': False,
                'error': f"Missing required parameters: {', '.join(missing_params)}",
                'data': [],
                'required_params': {
                    'lat': 'Latitude (-90 to 90)',
                    'lon': 'Longitude (-180 to 180)',
                    'start': 'Start date (YYYYMMDD)',
                    'end': 'End date (YYYYMMDD)'
                }
            }), 400
        
        # Convert coordinates to float
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid coordinate values. Latitude and longitude must be numeric.',
                'data': []
            }), 400
        
        # Log the request
        logger.info(f"NASA GPM API request: lat={lat}, lon={lon}, start={start}, end={end}")
        
        # Call the GPM precipitation service
        result = get_gpm_data(lat, lon, start, end)
        
        # Return appropriate HTTP status code
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Unexpected error in gpm-data endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred while processing your request.',
            'data': []
        }), 500

@api_bp.route('/modis-air')
def get_modis_air_quality_data():
    """
    Get NASA MODIS Aerosol Optical Depth (AOD) air quality data for specified location and date range.
    
    Query Parameters:
    - lat (float): Latitude (-90 to 90)
    - lon (float): Longitude (-180 to 180) 
    - start (string): Start date in YYYYMMDD format
    - end (string): End date in YYYYMMDD format
    
    Returns:
    - JSON with air quality data, aerosol index, health advisories, and metadata
    
    Air Quality Levels:
    - Good (AOD 0.0-0.1): Safe for all outdoor activities
    - Moderate (AOD 0.1-0.3): Acceptable for most people
    - Unhealthy for Sensitive (AOD 0.3-0.6): Sensitive groups should limit exposure
    - Unhealthy (AOD 0.6-1.0): Everyone should limit outdoor activities
    - Very Unhealthy (AOD 1.0-1.5): Health warnings for all
    - Hazardous (AOD >1.5): Emergency conditions
    """
    try:
        # Get required parameters
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        start = request.args.get('start')
        end = request.args.get('end')
        
        # Validate required parameters
        missing_params = []
        if not lat:
            missing_params.append('lat')
        if not lon:
            missing_params.append('lon')
        if not start:
            missing_params.append('start')
        if not end:
            missing_params.append('end')
        
        if missing_params:
            return jsonify({
                'success': False,
                'error': f"Missing required parameters: {', '.join(missing_params)}",
                'data': [],
                'required_params': {
                    'lat': 'Latitude (-90 to 90)',
                    'lon': 'Longitude (-180 to 180)',
                    'start': 'Start date (YYYYMMDD)',
                    'end': 'End date (YYYYMMDD)'
                }
            }), 400
        
        # Convert coordinates to float
        try:
            lat = float(lat)
            lon = float(lon)
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid coordinate values. Latitude and longitude must be numeric.',
                'data': []
            }), 400
        
        # Log the request
        logger.info(f"NASA MODIS Air Quality API request: lat={lat}, lon={lon}, start={start}, end={end}")
        
        # Call the MODIS air quality service
        result = get_modis_air_quality(lat, lon, start, end)
        
        # Return appropriate HTTP status code
        if result['success']:
            return jsonify(result)
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Unexpected error in modis-air endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred while processing your request.',
            'data': []
        }), 500

@api_bp.route('/worldview-image')
def get_worldview_image_data():
    """
    Get NASA Worldview satellite imagery for specified location and date.
    
    Query Parameters:
    - lat (float): Latitude (-90 to 90)
    - lon (float): Longitude (-180 to 180)
    - date (string): Date in YYYY-MM-DD format
    - layers (string): Comma-separated layer names (e.g., MODIS_Terra_CorrectedReflectance_TrueColor)
    - bbox_size (float, optional): Size of bounding box in degrees (default: 0.5)
    
    Returns:
    - JSON with image URL and metadata
    
    Common Layers:
    - MODIS_Terra_CorrectedReflectance_TrueColor: True color satellite imagery
    - MODIS_Aqua_CorrectedReflectance_TrueColor: Aqua satellite true color
    - MODIS_Terra_CorrectedReflectance_Bands721: False color (vegetation analysis)
    - VIIRS_SNPP_CorrectedReflectance_TrueColor: VIIRS true color imagery
    - MODIS_Terra_Aerosol: Aerosol optical depth visualization
    """
    try:
        # Get required parameters
        lat = request.args.get('lat')
        lon = request.args.get('lon')
        date = request.args.get('date')
        layers = request.args.get('layers')
        bbox_size = request.args.get('bbox_size', 0.5)
        
        # Validate required parameters
        missing_params = []
        if not lat:
            missing_params.append('lat')
        if not lon:
            missing_params.append('lon')
        if not date:
            missing_params.append('date')
        if not layers:
            missing_params.append('layers')
        
        if missing_params:
            return jsonify({
                'success': False,
                'error': f"Missing required parameters: {', '.join(missing_params)}",
                'image_url': None,
                'required_params': {
                    'lat': 'Latitude (-90 to 90)',
                    'lon': 'Longitude (-180 to 180)',
                    'date': 'Date (YYYY-MM-DD)',
                    'layers': 'Comma-separated layer names',
                    'bbox_size': 'Bounding box size in degrees (optional, default: 0.5)'
                },
                'available_layers': get_available_layers()
            }), 400
        
        # Convert coordinates and bbox_size to float
        try:
            lat = float(lat)
            lon = float(lon)
            bbox_size = float(bbox_size)
        except ValueError:
            return jsonify({
                'success': False,
                'error': 'Invalid numeric values. Latitude, longitude, and bbox_size must be numeric.',
                'image_url': None
            }), 400
        
        # Log the request
        logger.info(f"NASA Worldview API request: lat={lat}, lon={lon}, date={date}, layers={layers}")
        
        # Call the Worldview service
        result = get_worldview_image(lat, lon, date, layers, bbox_size)
        
        # Return appropriate HTTP status code
        if result['success']:
            return jsonify({
                'success': True,
                'date': result['date'],
                'layers': result['layers'],
                'image_url': result['image_url'],
                'location': result['location'],
                'bbox': result['bbox'],
                'metadata': result['metadata']
            })
        else:
            return jsonify({
                'success': False,
                'error': result['error'],
                'image_url': None
            }), 400
            
    except Exception as e:
        logger.error(f"Unexpected error in worldview-image endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred while processing your request.',
            'image_url': None
        }), 500

@api_bp.route('/worldview-layers')
def get_worldview_layers():
    """
    Get available NASA Worldview layers.
    
    Returns:
    - JSON with available layer information
    """
    try:
        layers = get_available_layers()
        return jsonify({
            'success': True,
            'layers': layers,
            'layer_count': len(layers)
        })
    except Exception as e:
        logger.error(f"Error in worldview-layers endpoint: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to retrieve available layers',
            'layers': {}
        }), 500
