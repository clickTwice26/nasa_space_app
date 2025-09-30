from functools import wraps
from flask import request, jsonify
import re

def validate_json(f):
    """Decorator to validate JSON request data"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_json:
            return jsonify({'error': 'Content-Type must be application/json'}), 400
        return f(*args, **kwargs)
    return decorated_function

def validate_coordinates(lat, lon):
    """Validate latitude and longitude coordinates"""
    try:
        lat = float(lat)
        lon = float(lon)
        
        if not (-90 <= lat <= 90):
            return False, "Latitude must be between -90 and 90"
        if not (-180 <= lon <= 180):
            return False, "Longitude must be between -180 and 180"
        
        return True, None
    except (ValueError, TypeError):
        return False, "Invalid coordinate format"

def validate_date_format(date_string):
    """Validate date format (YYYY-MM-DD)"""
    if not date_string:
        return True, None
    
    pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(pattern, date_string):
        return False, "Date must be in YYYY-MM-DD format"
    
    return True, None

def paginate_query(query, page=1, per_page=50, max_per_page=100):
    """Helper function for query pagination"""
    per_page = min(per_page, max_per_page)
    
    try:
        pagination = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return {
            'items': pagination.items,
            'pagination': {
                'page': pagination.page,
                'per_page': pagination.per_page,
                'total': pagination.total,
                'pages': pagination.pages,
                'has_next': pagination.has_next,
                'has_prev': pagination.has_prev
            }
        }
    except Exception as e:
        return None

def format_error_response(message, status_code=400):
    """Format consistent error responses"""
    return jsonify({
        'error': message,
        'status_code': status_code
    }), status_code

def format_success_response(data, message=None):
    """Format consistent success responses"""
    response = {'data': data}
    if message:
        response['message'] = message
    return jsonify(response)