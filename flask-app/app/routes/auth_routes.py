from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, flash
from app.services.auth_service import AuthService, OnboardingService, ProfileService
from functools import wraps
import logging

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def login_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        session_id = session.get('session_id')
        
        if not session_id:
            if request.is_json:
                return jsonify({'success': False, 'message': 'Authentication required'}), 401
            return redirect(url_for('auth.login'))
        
        # Validate session
        result = AuthService.get_session(session_id)
        if not result['success']:
            session.clear()
            if request.is_json:
                return jsonify({'success': False, 'message': 'Session expired'}), 401
            return redirect(url_for('auth.login'))
        
        # Add user to request context
        request.current_user = result['user']
        return f(*args, **kwargs)
    
    return decorated_function


def onboarding_required(f):
    """Decorator to require completed onboarding"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        user = request.current_user
        
        if not user['onboarding_completed']:
            if request.is_json:
                return jsonify({
                    'success': False, 
                    'message': 'Onboarding required',
                    'redirect': '/onboarding'
                }), 403
            return redirect(url_for('main.onboarding'))
        
        return f(*args, **kwargs)
    
    return decorated_function


# Routes for authentication pages
@auth_bp.route('/login')
def login():
    """Login page"""
    # If already logged in, redirect to dashboard
    session_id = session.get('session_id')
    if session_id:
        result = AuthService.get_session(session_id)
        if result['success']:
            return redirect(url_for('main.dashboard'))
    
    return render_template('auth/login.html')


@auth_bp.route('/register')
def register():
    """Registration page"""
    # If already logged in, redirect to dashboard
    session_id = session.get('session_id')
    if session_id:
        result = AuthService.get_session(session_id)
        if result['success']:
            return redirect(url_for('main.dashboard'))
    return render_template('auth/register_wizard.html')


@auth_bp.route('/logout')
def logout():
    """Logout page"""
    session_id = session.get('session_id')
    if session_id:
        AuthService.logout_session(session_id)
    
    session.clear()
    flash('You have been logged out successfully', 'info')
    return redirect(url_for('auth.login'))


# API Routes for authentication
@auth_bp.route('/api/register/start', methods=['POST'])
def api_register_start():
    """Start multi-step registration (creates user record and auto-login)"""
    try:
        data = request.get_json() or {}
        for field in ['email', 'username', 'password']:
            if not data.get(field):
                return jsonify({'success': False, 'message': f'{field.capitalize()} is required'}), 400
        result = AuthService.register_user(
            email=data['email'],
            username=data['username'],
            password=data['password']
        )
        if result['success']:
            logger.info(f"User registered (start wizard): {data['email']}")
            # Auto-login: create session for the new user
            user = result['user']
            session_result = AuthService.create_session(user_id=user['id'], expires_hours=24)
            if session_result['success']:
                session['session_id'] = session_result['session_id']
                session['user_id'] = user['id']
                result['session_id'] = session_result['session_id']
            return jsonify(result), 201
        return jsonify(result), 400
    except Exception as e:
        logger.error(f"Registration start error: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error starting registration'}), 500

@auth_bp.route('/api/register/role', methods=['POST'])
def api_register_role():
    """Set user role (requires session)"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        result = AuthService.get_session(session_id)
        if not result['success']:
            return jsonify({'success': False, 'message': 'Session invalid'}), 401
        user_dict = result['user']
        user_obj = AuthService._get_user_by_id(user_dict['id']) if hasattr(AuthService, '_get_user_by_id') else None
        # Fallback manual import to get live model instance
        from app.models.user import User
        if not user_obj:
            user_obj = User.query.get(user_dict['id'])
        data = request.get_json() or {}
        role = data.get('role')
        AuthService.set_user_role(user_obj, role)
        return jsonify({'success': True, 'user': user_obj.to_dict()}), 200
    except ValueError as ve:
        return jsonify({'success': False, 'message': str(ve)}), 400
    except Exception as e:
        logger.error(f"Registration role error: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error setting role'}), 500

@auth_bp.route('/api/register/location', methods=['POST'])
def api_register_location():
    """Set location data (requires session)"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        result = AuthService.get_session(session_id)
        if not result['success']:
            return jsonify({'success': False, 'message': 'Session invalid'}), 401
        user_dict = result['user']
        from app.models.user import User
        user_obj = User.query.get(user_dict['id'])
        data = request.get_json() or {}
        AuthService.set_user_location(user_obj, data)
        return jsonify({'success': True, 'user': user_obj.to_dict()}), 200
    except ValueError as ve:
        return jsonify({'success': False, 'message': str(ve)}), 400
    except Exception as e:
        logger.error(f"Registration location error: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error setting location'}), 500

@auth_bp.route('/api/register/complete', methods=['POST'])
def api_register_complete():
    """Finalize registration and mark onboarding complete (requires session)"""
    try:
        session_id = session.get('session_id')
        if not session_id:
            return jsonify({'success': False, 'message': 'Not authenticated'}), 401
        result = AuthService.get_session(session_id)
        if not result['success']:
            return jsonify({'success': False, 'message': 'Session invalid'}), 401
        user_dict = result['user']
        from app.models.user import User
        user_obj = User.query.get(user_dict['id'])
        AuthService.complete_registration(user_obj)
        return jsonify({'success': True, 'user': user_obj.to_dict()}), 200
    except Exception as e:
        logger.error(f"Registration complete error: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error completing registration'}), 500


@auth_bp.route('/api/login', methods=['POST'])
def api_login():
    """Authenticate user and create session"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        # Required fields
        if 'email_or_username' not in data or 'password' not in data:
            return jsonify({
                'success': False,
                'message': 'Email/username and password are required'
            }), 400
        
        # Authenticate user
        auth_result = AuthService.authenticate_user(
            email_or_username=data['email_or_username'],
            password=data['password']
        )
        
        if not auth_result['success']:
            return jsonify(auth_result), 401
        
        # Create session
        user = auth_result['user']
        session_result = AuthService.create_session(
            user_id=user['id'],
            expires_hours=24 * 7 if data.get('remember_me') else 24
        )
        
        if not session_result['success']:
            return jsonify(session_result), 500
        
        # Store session in Flask session
        session['session_id'] = session_result['session_id']
        session['user_id'] = user['id']
        session.permanent = data.get('remember_me', False)
        
        logger.info(f"User logged in: {user['email']}")
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user,
            'session_id': session_result['session_id'],
            'redirect': '/onboarding' if not user['onboarding_completed'] else '/dashboard'
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Login failed due to server error'
        }), 500


@auth_bp.route('/api/logout', methods=['POST'])
@login_required
def api_logout():
    """Logout current session"""
    try:
        session_id = session.get('session_id')
        
        if session_id:
            result = AuthService.logout_session(session_id)
            if not result['success']:
                logger.warning(f"Logout warning: {result['message']}")
        
        session.clear()
        
        return jsonify({
            'success': True,
            'message': 'Logged out successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Logout failed'
        }), 500


@auth_bp.route('/api/session', methods=['GET'])
def api_session():
    """Get current session information"""
    try:
        session_id = session.get('session_id')
        
        if not session_id:
            return jsonify({
                'success': False,
                'message': 'No active session',
                'authenticated': False
            }), 401
        
        result = AuthService.get_session(session_id)
        
        if result['success']:
            return jsonify({
                'success': True,
                'authenticated': True,
                'user': result['user'],
                'session': result['session']
            }), 200
        else:
            session.clear()
            return jsonify({
                'success': False,
                'message': result['message'],
                'authenticated': False
            }), 401
            
    except Exception as e:
        logger.error(f"Session check error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Session check failed',
            'authenticated': False
        }), 500


@auth_bp.route('/api/profile', methods=['GET'])
@login_required
def api_get_profile():
    """Get user profile"""
    try:
        user = request.current_user
        
        result = ProfileService.get_user_profile(user['id'])
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 404
            
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get profile'
        }), 500


@auth_bp.route('/api/profile', methods=['PUT'])
@login_required
def api_update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        user = request.current_user
        
        if not data:
            return jsonify({'success': False, 'message': 'No data provided'}), 400
        
        result = ProfileService.update_profile(user['id'], data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Update profile error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to update profile'
        }), 500


# Onboarding API Routes
@auth_bp.route('/api/onboarding/progress', methods=['GET'])
@login_required
def api_onboarding_progress():
    """Get onboarding progress"""
    try:
        user = request.current_user
        
        result = OnboardingService.get_onboarding_progress(user['id'])
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        logger.error(f"Onboarding progress error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to get onboarding progress'
        }), 500


@auth_bp.route('/api/onboarding/step', methods=['POST'])
@login_required
def api_onboarding_step():
    """Update onboarding step"""
    try:
        data = request.get_json()
        user = request.current_user
        
        if not data or 'step' not in data:
            return jsonify({
                'success': False,
                'message': 'Step name is required'
            }), 400
        
        result = OnboardingService.update_onboarding_step(
            user_id=user['id'],
            step_name=data['step'],
            data=data.get('data')
        )
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Onboarding step error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to update onboarding step'
        }), 500


@auth_bp.route('/api/onboarding/complete', methods=['POST'])
@login_required
def api_onboarding_complete():
    """Complete onboarding"""
    try:
        user = request.current_user
        
        result = OnboardingService.complete_onboarding(user['id'])
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Complete onboarding error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to complete onboarding'
        }), 500


# Utility function to check authentication status
def is_authenticated():
    """Check if user is authenticated"""
    session_id = session.get('session_id')
    if not session_id:
        return False
    
    result = AuthService.get_session(session_id)
    return result['success']


def get_current_user():
    """Get current authenticated user"""
    session_id = session.get('session_id')
    if not session_id:
        return None
    
    result = AuthService.get_session(session_id)
    if result['success']:
        return result['user']
    
    return None