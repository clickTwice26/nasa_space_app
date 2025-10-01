from app import create_app
import os

# Create Flask application instance
app = create_app()

if __name__ == '__main__':
    # Development server configuration
    debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    
    print(f"🚀 Starting NASA Space App on {host}:{port}")
    print(f"Debug mode: {debug_mode}")
    print(f"Database: {app.config['SQLALCHEMY_DATABASE_URI']}")
    
    app.run(
        debug=debug_mode,
        host=host,
        port=8080
    )