# Machine Learning Project

A comprehensive machine learning project for NASA space data analysis.

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

3. Start Jupyter notebook:
```bash
jupyter notebook
```

## Project Structure

```
ml-project/
├── src/                    # Source code
│   ├── data_processor.py   # Data processing utilities
│   ├── models.py          # ML models
│   └── utils.py           # Helper functions
├── notebooks/             # Jupyter notebooks
├── data/                  # Data directories
│   ├── raw/              # Raw data
│   └── processed/        # Processed data
├── models/               # Saved models
├── results/              # Results and outputs
└── tests/                # Test files
```

## Features

- Data preprocessing and cleaning
- Multiple ML algorithms (Random Forest, SVM, Linear models)
- Hyperparameter tuning with GridSearchCV
- Model evaluation and visualization
- Feature importance analysis
- Model persistence with joblib

## Usage

1. Place your data in the `data/raw/` directory
2. Use the notebooks for exploratory data analysis
3. Run training scripts from the `src/` directory
4. Saved models will be stored in the `models/` directory
5. Results and visualizations in the `results/` directory