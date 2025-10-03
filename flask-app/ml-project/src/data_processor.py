import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report
import joblib
import os
from datetime import datetime

class NASADataProcessor:
    """
    A class for processing NASA space-related data
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.model = None
        
    def load_data(self, file_path):
        """Load data from file"""
        try:
            if file_path.endswith('.csv'):
                data = pd.read_csv(file_path)
            elif file_path.endswith('.json'):
                data = pd.read_json(file_path)
            else:
                raise ValueError("Unsupported file format")
            
            print(f"Data loaded successfully. Shape: {data.shape}")
            return data
        except Exception as e:
            print(f"Error loading data: {e}")
            return None
    
    def preprocess_data(self, data, target_column=None):
        """Preprocess the data"""
        # Handle missing values
        data = data.dropna()
        
        # Separate features and target
        if target_column:
            X = data.drop(columns=[target_column])
            y = data[target_column]
        else:
            X = data
            y = None
        
        # Scale numerical features
        numerical_cols = X.select_dtypes(include=[np.number]).columns
        X_scaled = X.copy()
        X_scaled[numerical_cols] = self.scaler.fit_transform(X[numerical_cols])
        
        return X_scaled, y
    
    def save_model(self, model, model_name):
        """Save trained model"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{model_name}_{timestamp}.joblib"
        filepath = os.path.join("models", filename)
        
        os.makedirs("models", exist_ok=True)
        joblib.dump(model, filepath)
        print(f"Model saved: {filepath}")
        
    def load_model(self, model_path):
        """Load trained model"""
        try:
            self.model = joblib.load(model_path)
            print(f"Model loaded: {model_path}")
            return self.model
        except Exception as e:
            print(f"Error loading model: {e}")
            return None

if __name__ == "__main__":
    processor = NASADataProcessor()
    print("🚀 NASA Data Processor initialized")
    print("Ready for space data analysis!")