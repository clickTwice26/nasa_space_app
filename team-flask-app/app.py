from flask import Flask, render_template_string, send_from_directory
import os

app = Flask(__name__)

@app.route('/')
def home():
    """Serve the main team website"""
    try:
        with open('index.html', 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except FileNotFoundError:
        return "Website file not found", 404

@app.route('/favicon.ico')
def favicon():
    """Serve favicon"""
    return '', 204

if __name__ == '__main__':
    port = int(os.environ.get('FLASK_PORT', 5000))
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    
    print(f"🚀 TerraPulse Team Website starting on http://{host}:{port}")
    print(f"🌐 Debug mode: {'ON' if debug else 'OFF'}")
    
    app.run(host=host, port=port, debug=debug)