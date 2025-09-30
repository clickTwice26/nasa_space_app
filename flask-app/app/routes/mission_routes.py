from flask import Blueprint, jsonify, request
from app.services.mission_service import MissionService

mission_bp = Blueprint('missions', __name__)

@mission_bp.route('/')
def get_missions():
    """Get all missions"""
    missions, error = MissionService.get_all_missions()
    
    if error:
        return jsonify({'error': error}), 500
    
    return jsonify({
        'missions': missions,
        'count': len(missions)
    })

@mission_bp.route('/<int:mission_id>')
def get_mission(mission_id):
    """Get mission by ID"""
    mission, error = MissionService.get_mission_by_id(mission_id)
    
    if error:
        return jsonify({'error': error}), 404 if error == "Mission not found" else 500
    
    return jsonify(mission)

@mission_bp.route('/', methods=['POST'])
def create_mission():
    """Create a new mission"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    # Validate required fields
    required_fields = ['name']
    for field in required_fields:
        if field not in data:
            return jsonify({'error': f'Missing required field: {field}'}), 400
    
    mission, error = MissionService.create_mission(data)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify(mission), 201

@mission_bp.route('/<int:mission_id>', methods=['PUT'])
def update_mission(mission_id):
    """Update an existing mission"""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    mission, error = MissionService.update_mission(mission_id, data)
    
    if error:
        return jsonify({'error': error}), 404 if error == "Mission not found" else 400
    
    return jsonify(mission)

@mission_bp.route('/<int:mission_id>', methods=['DELETE'])
def delete_mission(mission_id):
    """Delete a mission"""
    success, message = MissionService.delete_mission(mission_id)
    
    if not success:
        return jsonify({'error': message}), 404 if message == "Mission not found" else 500
    
    return jsonify({'message': message})

@mission_bp.route('/type/<string:mission_type>')
def get_missions_by_type(mission_type):
    """Get missions by type"""
    missions, error = MissionService.get_missions_by_type(mission_type)
    
    if error:
        return jsonify({'error': error}), 500
    
    return jsonify({
        'missions': missions,
        'count': len(missions),
        'mission_type': mission_type
    })

@mission_bp.route('/status/<string:status>')
def get_missions_by_status(status):
    """Get missions by status"""
    missions, error = MissionService.get_missions_by_status(status)
    
    if error:
        return jsonify({'error': error}), 500
    
    return jsonify({
        'missions': missions,
        'count': len(missions),
        'status': status
    })