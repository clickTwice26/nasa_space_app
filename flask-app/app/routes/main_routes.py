from flask import Blueprint, render_template

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Main landing page"""
    return render_template('index.html')

@main_bp.route('/missions')
def missions_page():
    """Missions dashboard page"""
    return render_template('missions.html')

@main_bp.route('/data')
def data_page():
    """Data explorer page"""
    return render_template('data.html')

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')