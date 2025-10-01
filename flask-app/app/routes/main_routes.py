from flask import Blueprint, render_template, jsonify, request, redirect, url_for, session
from app.routes.auth_routes import login_required, onboarding_required, is_authenticated, get_current_user

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
    return render_template('community.html')

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