# 🚀 NASA Space App

A comprehensive project structure for NASA space applications, featuring three main components: Flask web application, machine learning analysis, and dataset management.

## Project Structure

```
nasa_space_app/
├── flask-app/          # Minimalist Flask web application
├── ml-project/         # Machine learning analysis and models
├── dataset/           # Data storage and management
└── README.md          # This file
```

## Components

### 1. Flask Application (`flask-app/`)
A minimalist but well-structured Flask web application with:
- Modern Flask with latest packages
- Clean project structure
- RESTful API endpoints
- Responsive web interface
- Docker-ready configuration

**Key Features:**
- Health check endpoints
- NASA data API integration
- Modern CSS styling
- JavaScript frontend
- CORS support

### 2. Machine Learning Project (`ml-project/`)
Comprehensive ML framework for space data analysis:
- Data preprocessing utilities
- Multiple ML algorithms
- Jupyter notebook environment
- Model evaluation tools
- Feature analysis

**Key Features:**
- Random Forest, SVM, Linear models
- Hyperparameter tuning
- Cross-validation
- Model persistence
- Visualization tools

### 3. Dataset (`dataset/`)
Organized data management system:
- Raw data storage
- Processed data
- External data sources
- Metadata management

**Key Features:**
- Structured data organization
- Multiple format support
- Data quality tracking
- Source documentation

## Quick Start

### Flask Application
```bash
cd flask-app
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

### Machine Learning
```bash
cd ml-project
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```

### Dataset Management
```bash
cd dataset
# Place your data in the appropriate directories
# Update metadata as needed
```

## Technologies Used

- **Backend:** Flask, Python 3.8+
- **ML:** scikit-learn, TensorFlow, PyTorch
- **Data:** pandas, NumPy, matplotlib
- **Frontend:** HTML5, CSS3, JavaScript
- **Tools:** Jupyter, pytest, Docker

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- NASA Open Data Portal
- NASA API services
- Open source community

---

*Ready for space exploration! 🛸*