from flask import Flask, render_template, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
    
    # Enable CORS
    CORS(app)
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/api/health')
    def health_check():
        return jsonify({'status': 'healthy', 'message': 'NASA Space App is running!'})
    
    @app.route('/api/data')
    def get_data():
        # Placeholder for NASA data endpoint
        return jsonify({
            'message': 'NASA Space App Data',
            'data': []
        })
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)