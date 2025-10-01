from flask import Blueprint, render_template, jsonify, request, redirect, url_for, session
from app.routes.auth_routes import login_required, onboarding_required, is_authenticated, get_current_user
from app.services.auth_service import AuthService
from app.models.user import User
from app import db
import logging

logger = logging.getLogger(__name__)

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main entry point - redirect based on authentication status"""
    if is_authenticated():
        user = get_current_user()
        if user and not user['onboarding_completed']:
            return redirect(url_for('main.onboarding'))
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/onboarding')
@login_required
def onboarding():
    """User onboarding flow"""
    user = get_current_user()
    if user and user['onboarding_completed']:
        return redirect(url_for('main.dashboard'))
    return render_template('onboarding.html')

@main_bp.route('/risk-dashboard')
def risk_dashboard():
    """Agricultural Risk Dashboard - Public demo page"""
    return render_template('risk_dashboard.html')

@main_bp.route('/dashboard')
@onboarding_required
def dashboard():
    """TerraPulse Dashboard"""
    return render_template('dashboard.html')

@main_bp.route('/predictions')
@onboarding_required
def predictions():
    """Environmental Predictions"""
    return render_template('predictions.html')

@main_bp.route('/data')
@onboarding_required
def data_page():
    """Data Insights & Analytics"""
    return render_template('data.html')

@main_bp.route('/community')
@onboarding_required
def community():
    """Agricultural Community Feed"""
    user = get_current_user()
    return render_template('community.html', user=user)

@main_bp.route('/discover')
@onboarding_required
def discover():
    """Discover communities page"""
    from app.services.community_service import CommunityService
    
    user = get_current_user()
    
    # Get suggested communities for discovery
    suggested_communities = CommunityService.get_suggested_communities(user['id'], limit=12)
    
    # Get popular communities
    popular_communities = CommunityService.get_popular_communities(limit=9)
    
    # Get community stats
    stats = CommunityService.get_community_stats()
    
    return render_template('discover.html', 
                         suggested_communities=suggested_communities,
                         popular_communities=popular_communities,
                         stats=stats,
                         user=user)

@main_bp.route('/settings')
@onboarding_required
def settings():
    """App Settings"""
    return render_template('settings.html')

@main_bp.route('/missions')
@onboarding_required
def missions_page():
    """Legacy missions page (keep for compatibility)"""
    return render_template('missions.html')

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@main_bp.route('/health')
def health_check():
    """Health check endpoint for TerraPulse"""
    return jsonify({
        'status': 'healthy',
        'service': 'TerraPulse',
        'version': '1.0.0',
        'description': 'Environmental Intelligence for Bangladesh'
    })


# API Routes for Profile Management
@main_bp.route('/api/profile/update', methods=['POST'])
@login_required
def update_profile():
    """Update user profile information"""
    try:
        user = get_current_user()
        data = request.get_json()
        
        # Get user from database
        db_user = User.query.filter_by(id=user['id']).first()
        if not db_user:
            return jsonify({'success': False, 'message': 'User not found'}), 404
        
        # Update profile fields
        if 'full_name' in data:
            db_user.full_name = data['full_name']
        if 'location' in data:
            db_user.location = data['location']
        if 'district' in data:
            db_user.district = data['district']
        if 'primary_crop' in data:
            db_user.primary_crop = data['primary_crop']
        if 'farm_size' in data:
            db_user.farm_size = float(data['farm_size']) if data['farm_size'] else None
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully'
        })
        
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'Failed to update profile'
        }), 500


@main_bp.route('/api/settings/notifications', methods=['POST'])
@login_required
def update_notification_settings():
    """Update notification preferences"""
    try:
        user = get_current_user()
        data = request.get_json()
        
        # For now, we'll store notification settings in session
        # In a real app, you'd add notification columns to the User model
        session['notification_settings'] = data
        
        return jsonify({
            'success': True,
            'message': 'Notification settings updated'
        })
        
    except Exception as e:
        logger.error(f"Notification settings error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to update notification settings'
        }), 500


@main_bp.route('/api/settings/preferences', methods=['POST'])
@login_required
def update_app_preferences():
    """Update app preferences like language, units, etc."""
    try:
        user = get_current_user()
        data = request.get_json()
        
        # Store app preferences in session for now
        session['app_preferences'] = data
        
        return jsonify({
            'success': True,
            'message': 'App preferences updated'
        })
        
    except Exception as e:
        logger.error(f"App preferences error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Failed to update app preferences'
        }), 500