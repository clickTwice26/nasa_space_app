import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.svm import SVC, SVR
from sklearn.model_selection import cross_val_score, GridSearchCV
from sklearn.metrics import accuracy_score, mean_squared_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns

class NASAMLModels:
    """
    Machine Learning models for NASA space data analysis
    """
    
    def __init__(self):
        self.models = {}
        self.best_params = {}
        
    def train_classification_model(self, X_train, y_train, model_type='random_forest'):
        """Train classification model"""
        
        if model_type == 'random_forest':
            model = RandomForestClassifier(n_estimators=100, random_state=42)
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, None],
                'min_samples_split': [2, 5, 10]
            }
        elif model_type == 'logistic_regression':
            model = LogisticRegression(random_state=42)
            param_grid = {
                'C': [0.1, 1, 10],
                'solver': ['liblinear', 'lbfgs']
            }
        elif model_type == 'svm':
            model = SVC(random_state=42)
            param_grid = {
                'C': [0.1, 1, 10],
                'kernel': ['rbf', 'linear']
            }
        else:
            raise ValueError("Unsupported model type")
        
        # Grid search for best parameters
        grid_search = GridSearchCV(model, param_grid, cv=5, scoring='accuracy')
        grid_search.fit(X_train, y_train)
        
        self.models[model_type] = grid_search.best_estimator_
        self.best_params[model_type] = grid_search.best_params_
        
        print(f"{model_type} trained successfully!")
        print(f"Best parameters: {grid_search.best_params_}")
        print(f"Best CV score: {grid_search.best_score_:.4f}")
        
        return grid_search.best_estimator_
    
    def train_regression_model(self, X_train, y_train, model_type='random_forest'):
        """Train regression model"""
        
        if model_type == 'random_forest':
            model = RandomForestRegressor(n_estimators=100, random_state=42)
            param_grid = {
                'n_estimators': [50, 100, 200],
                'max_depth': [5, 10, None]
            }
        elif model_type == 'linear_regression':
            model = LinearRegression()
            param_grid = {}  # No hyperparameters to tune
        elif model_type == 'svr':
            model = SVR()
            param_grid = {
                'C': [0.1, 1, 10],
                'kernel': ['rbf', 'linear']
            }
        else:
            raise ValueError("Unsupported model type")
        
        if param_grid:
            grid_search = GridSearchCV(model, param_grid, cv=5, scoring='r2')
            grid_search.fit(X_train, y_train)
            best_model = grid_search.best_estimator_
            best_params = grid_search.best_params_
            best_score = grid_search.best_score_
        else:
            model.fit(X_train, y_train)
            best_model = model
            best_params = {}
            best_score = model.score(X_train, y_train)
        
        self.models[model_type] = best_model
        self.best_params[model_type] = best_params
        
        print(f"{model_type} trained successfully!")
        print(f"Best parameters: {best_params}")
        print(f"Best CV score: {best_score:.4f}")
        
        return best_model
    
    def evaluate_model(self, model, X_test, y_test, task_type='classification'):
        """Evaluate model performance"""
        
        predictions = model.predict(X_test)
        
        if task_type == 'classification':
            accuracy = accuracy_score(y_test, predictions)
            print(f"Accuracy: {accuracy:.4f}")
            print("\nClassification Report:")
            print(classification_report(y_test, predictions))
            return accuracy
        else:
            mse = mean_squared_error(y_test, predictions)
            r2 = r2_score(y_test, predictions)
            print(f"Mean Squared Error: {mse:.4f}")
            print(f"R² Score: {r2:.4f}")
            return r2
    
    def plot_feature_importance(self, model, feature_names, model_name):
        """Plot feature importance for tree-based models"""
        
        if hasattr(model, 'feature_importances_'):
            importance = model.feature_importances_
            indices = np.argsort(importance)[::-1]
            
            plt.figure(figsize=(10, 6))
            plt.title(f"Feature Importance - {model_name}")
            plt.bar(range(len(importance)), importance[indices])
            plt.xticks(range(len(importance)), [feature_names[i] for i in indices], rotation=45)
            plt.tight_layout()
            plt.show()
        else:
            print("Model doesn't support feature importance")

if __name__ == "__main__":
    ml_models = NASAMLModels()
    print("🚀 NASA ML Models initialized")
    print("Ready for space data modeling!")