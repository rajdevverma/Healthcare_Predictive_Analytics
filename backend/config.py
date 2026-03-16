"""
Configuration settings for Healthcare Predictive Analytics System
"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'healthcare_predictive_analytics_2026')
    DEBUG = False
    TESTING = False
    
    # Database Configuration
    DB_TYPE = 'mysql'
    
    # MySQL Configuration
    MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.getenv('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', '')
    MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'healthcare_db')
    
    # ML Models Configuration
    ML_MODELS_PATH = os.path.join(os.path.dirname(__file__), 'ml_models')
    HEART_MODEL_PATH = os.path.join(ML_MODELS_PATH, 'heart_disease_rf.pkl')
    DIABETES_MODEL_PATH = os.path.join(ML_MODELS_PATH, 'diabetes_rf.pkl')
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt_healthcare_secret_2026')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    
    # Pagination
    ITEMS_PER_PAGE = 10

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    ENV = 'production'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
