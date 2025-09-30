# NASA Space App - Flask Application

A comprehensive Flask application with SQLite database, organized using blueprints for NASA space-related data management and analysis.

## 🏗️ Architecture

This application follows modern Flask best practices with:
- **Application Factory Pattern** for configuration management
- **Blueprints** for organized route separation
- **SQLAlchemy ORM** with SQLite database
- **Service Layer** for business logic separation
- **Marshmallow** for data serialization
- **Flask-Migrate** for database migrations

## 📁 Project Structure

```
flask-app/
├── app/
│   ├── __init__.py          # Application factory
│   ├── models/              # Database models
│   │   └── __init__.py      # Mission, DataRecord, Spacecraft models
│   ├── routes/              # Blueprint routes
│   │   ├── main_routes.py   # Main web pages
│   │   ├── api_routes.py    # General API endpoints
│   │   └── mission_routes.py # Mission-specific API
│   ├── services/            # Business logic layer
│   │   ├── mission_service.py
│   │   └── data_service.py
│   ├── utils/               # Utility functions
│   │   └── helpers.py       # Validation and helper functions
│   ├── templates/           # Jinja2 templates
│   │   ├── index.html
│   │   ├── missions.html
│   │   └── data.html
│   └── static/              # CSS, JS, images
│       ├── css/style.css
│       └── js/
│           ├── main.js
│           ├── missions.js
│           └── data.js
├── instance/                # SQLite database location
├── migrations/              # Database migration files
├── tests/                   # Test files
├── app.py                   # Application entry point
├── init_db.py              # Database initialization script
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## 🚀 Quick Start

### 1. Set up the environment

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings (optional for development)
```

### 3. Initialize the database

```bash
# Create database and add sample data
python init_db.py
```

### 4. Run the application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## 🗄️ Database Models

### Mission
- NASA missions tracking
- Fields: name, description, launch_date, status, mission_type, agency

### DataRecord
- Data records from missions
- Fields: mission_id, record_type, data_source, timestamp, coordinates, data_values

### Spacecraft
- Spacecraft/satellite information
- Fields: name, norad_id, mission_id, spacecraft_type, status, specifications

## 🔗 API Endpoints

### General
- `GET /api/health` - Health check
- `GET /api/stats` - Data statistics

### Missions (`/api/missions/`)
- `GET /` - List all missions
- `POST /` - Create new mission
- `GET /{id}` - Get mission by ID
- `PUT /{id}` - Update mission
- `DELETE /{id}` - Delete mission
- `GET /type/{type}` - Get missions by type
- `GET /status/{status}` - Get missions by status

### Data (`/api/data`)
- `GET /` - List data records (paginated)
- `POST /` - Create data record
- `GET /mission/{id}` - Data by mission
- `GET /type/{type}` - Data by record type
- `GET /location` - Data by geographic bounds

## 🌐 Web Interface

### Pages
- **Home** (`/`) - Overview and API documentation
- **Missions** (`/missions`) - Mission management interface
- **Data Explorer** (`/data`) - Data browsing and filtering
- **About** (`/about`) - Application information

### Features
- **Mission Management:** Create, edit, delete missions
- **Data Exploration:** Filter and browse data records
- **Responsive Design:** Works on desktop and mobile
- **Real-time API:** AJAX-powered interface

## 🧪 Development

### Database Operations

```bash
# Reset database
python init_db.py

# Add Flask-Migrate (if needed)
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Testing

```bash
# Run tests
pytest

# Run with coverage
pytest --cov=app
```

### Environment Variables

```env
SECRET_KEY=your-secret-key-here
FLASK_ENV=development
FLASK_DEBUG=True
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
DATABASE_URL=sqlite:///nasa_space_app.db
SQLALCHEMY_ECHO=True
```

## 📊 Sample Data

The `init_db.py` script creates sample data including:
- **5 NASA missions** (Artemis I, Mars 2020, Hubble, ISS, JWST)
- **3 spacecraft** with specifications
- **5 data records** with various types (images, telemetry, observations)

## 🔧 Technologies Used

- **Flask 3.0.0** - Web framework
- **SQLAlchemy 2.0.23** - Database ORM
- **Flask-Migrate 4.0.5** - Database migrations
- **Marshmallow 3.20.1** - Data serialization
- **Flask-CORS 4.0.0** - Cross-origin requests
- **SQLite** - Database engine

## 📈 Production Deployment

### Using Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Environment Setup

1. Set `FLASK_ENV=production`
2. Use a secure `SECRET_KEY`
3. Configure proper database URL
4. Set up reverse proxy (nginx)
5. Enable HTTPS

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Ready for space exploration! 🚀**