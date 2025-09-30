# Flask App

A minimalist Flask application with proper project structure for NASA Space App.

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your values
```

4. Run the application:
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## API Endpoints

- `GET /` - Main page
- `GET /api/health` - Health check
- `GET /api/data` - NASA data endpoint

## Project Structure

```
flask-app/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── .env.example       # Environment variables template
├── app/
│   ├── templates/     # HTML templates
│   └── static/        # CSS, JS, images
└── tests/             # Test files
```