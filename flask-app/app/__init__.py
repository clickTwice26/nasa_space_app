from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_marshmallow import Marshmallow
import os
from dotenv import load_dotenv

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()

def create_app(config_name='development'):
    """Application factory pattern"""
    
    # Load environment variables
    load_dotenv()
    
    # Create Flask app
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 
        'sqlite:///' + os.path.join(app.instance_path, 'nasa_space_app.db')
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = os.getenv('FLASK_ENV') == 'development'
    
    # Session configuration for proper cookie handling
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours
    
    # Ensure instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)
    CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})
    
    # Register blueprints
    from app.routes.main_routes import main_bp
    from app.routes.api_routes import api_bp
    from app.routes.mission_routes import mission_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.community_routes import community_bp
    from app.routes.risk import risk_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(mission_bp, url_prefix='/missions')
    app.register_blueprint(auth_bp)
    app.register_blueprint(community_bp)
    app.register_blueprint(risk_bp, url_prefix='/api')
    
    # Context processor to make user data available to all templates
    @app.context_processor
    def inject_user():
        from app.routes.auth_routes import get_current_user
        try:
            user = get_current_user()
            return dict(user=user)
        except:
            return dict(user=None)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app