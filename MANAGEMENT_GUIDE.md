# NASA Space App Management Documentation

## 🚀 Project Management Script

The `manage.py` script is a comprehensive, modular management tool for the entire NASA Space App project. It provides unified control over all three sub-projects: Flask application, ML project, and dataset management.

## 📋 Quick Start

```bash
# Check project status
python manage.py status

# Complete project setup
python manage.py setup

# Setup individual components
python manage.py setup --component flask
python manage.py setup --component ml
python manage.py setup --component dataset
```

## 🔧 Flask Application Commands

### Setup and Database Operations

```bash
# Setup Flask application
python manage.py flask setup

# Initialize database with sample data
python manage.py flask init-db

# Reset database (removes existing data)
python manage.py flask init-db --reset

# Run database migration
python manage.py flask migrate --message "Your migration message"
```

### Development Server

```bash
# Run development server (default port 6767)
python manage.py flask run

# Run on custom port and host
python manage.py flask run --port 8080 --host 127.0.0.1

# Run without debug mode
python manage.py flask run --no-debug
```

### Testing

```bash
# Run Flask application tests
python manage.py flask test
```

## 🤖 Machine Learning Commands

### Setup and Environment

```bash
# Setup ML project environment
python manage.py ml setup

# Start Jupyter notebook server
python manage.py ml jupyter

# Start Jupyter on custom port
python manage.py ml jupyter --port 9999
```

### Training and Execution

```bash
# Run training script
python manage.py ml train data_processor.py
python manage.py ml train models.py
```

## 📊 Dataset Management Commands

### Structure and Validation

```bash
# Validate dataset directory structure
python manage.py dataset validate

# Generate dataset catalog
python manage.py dataset catalog
```

## 🔍 Status and Monitoring

### Project Status

```bash
# Check overall project status
python manage.py status
```

Example output:
```
🚀 NASA Space App Project Status

📂 Flask Application
  Virtual Environment: ✅
  Requirements Installed: ✅
  Database: ✅
  App File: ✅
  Database Tables: missions, data_records, spacecraft

📂 Machine Learning Project
  Virtual Environment: ✅
  Notebooks: 3 files
  Models: 2 files
  Data Files: 15 files

📂 Dataset
  Structure: ✅
  Raw: 8 files (45.2 MB)
  Processed: 5 files (23.1 MB)
  External: 2 files (12.8 MB)
```

## 🧹 Cleanup Operations

### Clean Project Files

```bash
# Clean all project virtual environments
python manage.py clean

# Clean specific component
python manage.py clean --component flask
python manage.py clean --component ml

# Force cleanup without confirmation
python manage.py clean --force
```

## 📚 Detailed Command Reference

### Complete Setup Workflow

For a brand new project setup:

```bash
# 1. Check current status
python manage.py status

# 2. Complete setup of all components
python manage.py setup

# 3. Initialize Flask database
python manage.py flask init-db

# 4. Validate dataset structure
python manage.py dataset validate

# 5. Generate dataset catalog
python manage.py dataset catalog

# 6. Start Flask development server
python manage.py flask run
```

### Development Workflow

Daily development commands:

```bash
# Start Flask server for web development
python manage.py flask run

# In another terminal, start Jupyter for ML work
python manage.py ml jupyter

# Run tests before committing
python manage.py flask test

# Check overall project status
python manage.py status
```

### Database Management

Working with Flask database:

```bash
# Create new migration after model changes
python manage.py flask migrate --message "Added new field to Mission model"

# Reset database and reload sample data
python manage.py flask init-db --reset

# Check database status
python manage.py status
```

## 🏗️ Architecture and Features

### Modular Design

The management script is built with a modular architecture:

- **ProjectManager**: Base class for common operations
- **FlaskManager**: Flask-specific operations
- **MLManager**: Machine learning project operations  
- **DatasetManager**: Dataset management operations
- **ProjectStatusChecker**: Cross-project status monitoring

### Key Features

1. **Virtual Environment Management**: Automatic creation and management
2. **Dependency Installation**: Automated requirements installation
3. **Database Operations**: Complete database lifecycle management
4. **Development Servers**: Easy server startup with configuration
5. **Status Monitoring**: Comprehensive project health checks
6. **Cross-Platform**: Works on Windows, macOS, and Linux
7. **Error Handling**: Robust error handling and user feedback
8. **Colored Output**: Enhanced terminal output with colors and emojis

### Extensibility

Adding new commands is straightforward:

1. Create a new manager class inheriting from `ProjectManager`
2. Add command-line arguments in the `main()` function
3. Implement command handlers
4. Add status checking methods

Example for adding a new component:

```python
class DeploymentManager(ProjectManager):
    def __init__(self):
        super().__init__(PROJECT_ROOT / "deployment")
    
    def deploy_to_cloud(self):
        """Deploy application to cloud"""
        Logger.section("Cloud Deployment")
        # Implementation here
        return True

# Add to main() function:
deploy_parser = subparsers.add_parser('deploy', help='Deployment operations')
# Add subcommands and handlers
```

## 🔧 Configuration

### Environment Variables

The script respects these environment variables:

- `FLASK_PORT`: Default port for Flask server
- `FLASK_HOST`: Default host for Flask server  
- `FLASK_DEBUG`: Debug mode setting
- `DATABASE_URL`: Database connection string

### Directory Structure

Expected project structure:
```
nasa_space_app/
├── manage.py              # Main management script
├── flask-app/             # Flask application
│   ├── venv/             # Virtual environment
│   ├── app.py            # Flask app
│   ├── init_db.py        # DB initialization
│   └── requirements.txt   # Dependencies
├── ml-project/            # ML project
│   ├── venv/             # Virtual environment
│   ├── src/              # Source code
│   ├── notebooks/        # Jupyter notebooks
│   └── requirements.txt   # Dependencies
└── dataset/               # Dataset management
    ├── raw/              # Raw data
    ├── processed/        # Processed data
    ├── external/         # External data
    └── metadata/         # Metadata files
```

## 🚨 Troubleshooting

### Common Issues

1. **Permission Denied**: Make sure script is executable (`chmod +x manage.py`)
2. **Python Not Found**: Ensure Python 3.6+ is installed
3. **Virtual Environment Issues**: Try cleaning and recreating (`python manage.py clean`)
4. **Port Already in Use**: Use different port (`--port` option)
5. **Database Locked**: Stop all Flask processes and retry

### Debug Mode

For detailed error information, check the terminal output. The script provides colored, descriptive error messages.

### Getting Help

```bash
# General help
python manage.py --help

# Command-specific help
python manage.py flask --help
python manage.py ml --help
python manage.py dataset --help
```

## 🎯 Best Practices

1. **Always check status first**: `python manage.py status`
2. **Use virtual environments**: Script manages them automatically
3. **Regular database backups**: Before running migrations
4. **Test before deployment**: Use `python manage.py flask test`
5. **Keep dependencies updated**: Regularly update requirements.txt files
6. **Use meaningful migration messages**: `--message` option for migrations
7. **Monitor project health**: Regular status checks

---

**Ready for comprehensive NASA space exploration! 🛸**