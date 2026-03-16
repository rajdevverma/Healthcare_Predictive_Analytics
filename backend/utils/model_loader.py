"""
ML Model Loader Utility
Dynamically loads and caches trained ML models
"""
import pickle
import os
import sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import config

class ModelLoader:
    """Singleton pattern for loading ML models"""
    _instance = None
    _models = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelLoader, cls).__new__(cls)
        return cls._instance
    
    def load_model(self, model_type='heart'):
        """
        Load ML model from disk
        
        Args:
            model_type: 'heart' or 'diabetes'
        
        Returns:
            Loaded scikit-learn model
        """
        # Return cached model if available
        if model_type in self._models:
            return self._models[model_type]
        
        cfg = config['development']()
        
        # Determine model path
        if model_type == 'heart':
            model_path = cfg.HEART_MODEL_PATH
        elif model_type == 'diabetes':
            model_path = cfg.DIABETES_MODEL_PATH
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Load model
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Model file not found: {model_path}")
        
        with open(model_path, 'rb') as f:
            model_data = pickle.load(f)
        
        # Handle both old and new format (with scaler bundled)
        if isinstance(model_data, dict):
            model = model_data['model']
            scaler = model_data.get('scaler')
        else:
            model = model_data
            scaler = None
        
        # Cache model and scaler
        self._models[model_type] = {'model': model, 'scaler': scaler}
        print(f"✓ Loaded {model_type} disease model from {model_path}")
        
        return self._models[model_type]
    
    def predict(self, model_type, features):
        """
        Make prediction using loaded model
        
        Args:
            model_type: 'heart' or 'diabetes'
            features: List or array of feature values
        
        Returns:
            dict with prediction, probability, risk_percentage, risk_level
        """
        model_data = self.load_model(model_type)
        
        # Extract model and scaler
        if isinstance(model_data, dict):
            model = model_data['model']
            scaler = model_data.get('scaler')
        else:
            model = model_data
            scaler = None
        
        # Convert to numpy array and reshape
        features_array = np.array(features).reshape(1, -1)
        
        # Apply scaling if scaler is available
        if scaler:
            features_array = scaler.transform(features_array)
        
        # Get prediction and probability
        prediction = model.predict(features_array)[0]
        probability = model.predict_proba(features_array)[0]
        
        # Calculate risk percentage (probability of positive class)
        risk_percentage = round(probability[1] * 100, 2)
        
        # Determine risk level
        if risk_percentage < 30:
            risk_level = "Low"
        elif risk_percentage < 70:
            risk_level = "Medium"
        else:
            risk_level = "High"
        
        return {
            'prediction': int(prediction),
            'probability': probability.tolist(),
            'risk_percentage': risk_percentage,
            'risk_level': risk_level
        }

# Global model loader instance
model_loader = ModelLoader()

def get_model_loader():
    """Helper function to get model loader instance"""
    return model_loader
