from flask import Blueprint, request, jsonify, session, redirect, url_for, render_template, flash
from functools import wraps
import logging
import uuid
import random
import string
from datetime import datetime

# Create blueprint
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function to generate random user data
def generate_random_user():
    """Generate random user credentials for session-based auth"""
    
    # Generate random username
    adjectives = ['Happy', 'Smart', 'Bright', 'Green', 'Solar', 'Earth', 'Ocean', 'Sky', 'Forest', 'River']
    nouns = ['Farmer', 'Gardener', 'Explorer', 'Guardian', 'Scientist', 'Pioneer', 'Keeper', 'Watcher', 'Friend', 'Helper']
    username = f"{random.choice(adjectives)}{random.choice(nouns)}{random.randint(100, 999)}"
    
    # Generate random email
    domains = ['terrapulse.com', 'earthwatch.com', 'greentech.com', 'climate.org', 'sustainability.net']
    email = f"{username.lower()}@{random.choice(domains)}"
    
    # Generate random full name
    first_names = ['Alex', 'Jordan', 'Taylor', 'Casey', 'Morgan', 'Riley', 'Avery', 'Jamie', 'Sage', 'River']
    last_names = ['Green', 'Earth', 'Forest', 'Field', 'Garden', 'Grove', 'Hill', 'Vale', 'Brook', 'Stone']
    full_name = f"{random.choice(first_names)} {random.choice(last_names)}"
    
    return {
        'id': str(uuid.uuid4()),
        'username': username,
        'email': email,
        'full_name': full_name,
        'created_at': datetime.now().isoformat(),
        'onboarding_completed': False,
        'profile_data': {}
    }

def get_current_user():
    """Get current user from session storage"""
    return session.get('user_data')

def is_authenticated():
    """Check if user is authenticated via session"""
    return session.get('user_data') is not None

def login_required(f):
    """Decorator to require session-based authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_authenticated():
            # Create temporary user for session
            user_data = generate_random_user()
            session['user_data'] = user_data
            session.permanent = True
            logger.info(f"Created temporary user: {user_data['username']}")
            
            # Redirect to onboarding for new users
            if request.is_json:
                return jsonify({
                    'success': False, 
                    'message': 'Onboarding required',
                    'redirect': '/onboarding'
                }), 403
            return redirect(url_for('main.onboarding'))
        
        # Add user to request context
        request.current_user = session['user_data']
        return f(*args, **kwargs)
    
    return decorated_function
    
    return decorated_function


def onboarding_required(f):
    """Decorator to require completed onboarding - now optional"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        
        if not user:
            # Create temporary user
            user_data = generate_random_user()
            session['user_data'] = user_data
            session.permanent = True
            return redirect(url_for('main.onboarding'))
        
        # Allow access regardless of onboarding status
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated_function


# API Routes for session-based auth
@auth_bp.route('/start-session', methods=['POST'])
def start_session():
    """Start a new temporary session"""
    try:
        user_data = generate_random_user()
        session['user_data'] = user_data
        session.permanent = True
        
        logger.info(f"Started new session for user: {user_data['username']}")
        
        return jsonify({
            'success': True,
            'message': 'Session started successfully',
            'user': {
                'username': user_data['username'],
                'email': user_data['email'],
                'full_name': user_data['full_name']
            }
        })
    except Exception as e:
        logger.error(f"Error starting session: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to start session'
        }), 500

@auth_bp.route('/update-profile', methods=['POST'])
def update_profile():
    """Update user profile in session"""
    try:
        user_data = get_current_user()
        if not user_data:
            return jsonify({
                'success': False,
                'message': 'No active session'
            }), 401
        
        # Get profile data from request
        profile_update = request.json
        
        # Update profile data
        user_data['profile_data'].update(profile_update)
        
        # Update specific fields if provided
        if 'full_name' in profile_update:
            user_data['full_name'] = profile_update['full_name']
        
        # Save back to session
        session['user_data'] = user_data
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'user': user_data
        })
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to update profile'
        }), 500

@auth_bp.route('/complete-onboarding', methods=['POST'])
def complete_onboarding():
    """Mark onboarding as completed"""
    try:
        user_data = get_current_user()
        if not user_data:
            return jsonify({
                'success': False,
                'message': 'No active session'
            }), 401
        
        user_data['onboarding_completed'] = True
        session['user_data'] = user_data
        
        return jsonify({
            'success': True,
            'message': 'Onboarding completed successfully'
        })
    except Exception as e:
        logger.error(f"Error completing onboarding: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to complete onboarding'
        }), 500


@auth_bp.route('/logout')
def logout():
    """Clear session"""
    session.clear()
    return redirect(url_for('main.index'))

@auth_bp.route('/status')
def auth_status():
    """Get current authentication status"""
    user = get_current_user()
    return jsonify({
        'authenticated': user is not None,
        'user': user if user else None
    })

# Legacy routes for backwards compatibility - now redirect to main app
@auth_bp.route('/login')
def login():
    """Legacy login route - redirect to main app"""
    return redirect(url_for('main.index'))

@auth_bp.route('/register') 
def register():
    """Legacy register route - redirect to onboarding"""
    return redirect(url_for('main.onboarding'))


# Additional utility functions for backwards compatibility
def is_authenticated():
    """Check if user is authenticated via session"""
    return session.get('user_data') is not None