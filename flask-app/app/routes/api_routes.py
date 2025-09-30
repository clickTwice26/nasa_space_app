from flask import Blueprint, jsonify, request
from app.services.data_service import DataService

api_bp = Blueprint('api', __name__)

@api_bp.route('/health')
def health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'message': 'NASA Space App API is running!',
        'version': '1.0.0'
    })

@api_bp.route('/data')
def get_data():
    """Get data records with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    
    # Limit per_page to prevent abuse
    per_page = min(per_page, 100)
    
    data, error = DataService.get_all_data_records(page, per_page)
    
    if error:
        return jsonify({'error': error}), 500
    
    return jsonify(data)

@api_bp.route('/data/mission/<int:mission_id>')
def get_data_by_mission(mission_id):
    """Get data records for a specific mission"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    per_page = min(per_page, 100)
    
    data, error = DataService.get_data_by_mission(mission_id, page, per_page)
    
    if error:
        return jsonify({'error': error}), 500
    
    return jsonify(data)

@api_bp.route('/data/type/<string:record_type>')
def get_data_by_type(record_type):
    """Get data records by type"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    per_page = min(per_page, 100)
    
    data, error = DataService.get_data_by_type(record_type, page, per_page)
    
    if error:
        return jsonify({'error': error}), 500
    
    return jsonify(data)

@api_bp.route('/data/location')
def get_data_by_location():
    """Get data records by geographic bounds"""
    try:
        lat_min = float(request.args.get('lat_min', -90))
        lat_max = float(request.args.get('lat_max', 90))
        lon_min = float(request.args.get('lon_min', -180))
        lon_max = float(request.args.get('lon_max', 180))
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        per_page = min(per_page, 100)
        
        data, error = DataService.get_data_by_location(
            lat_min, lat_max, lon_min, lon_max, page, per_page
        )
        
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify(data)
    
    except ValueError:
        return jsonify({'error': 'Invalid coordinate parameters'}), 400

@api_bp.route('/data', methods=['POST'])
def create_data_record():
    """Create a new data record"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    result, error = DataService.create_data_record(data)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify(result), 201

@api_bp.route('/stats')
def get_statistics():
    """Get basic statistics about the data"""
    stats, error = DataService.get_data_statistics()
    
    if error:
        return jsonify({'error': error}), 500
    
    return jsonify(stats)