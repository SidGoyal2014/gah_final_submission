import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask Configuration
    FLASK_ENV = os.environ.get('FLASK_ENV')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    PORT = os.environ.get('PORT')

    # Database Configuration - Cloud SQL optimized
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    
    # Cloud SQL specific engine options
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Verify connections before use
        'pool_recycle': 300,    # Recycle connections every 5 minutes
        'pool_timeout': 20,     # Wait up to 20 seconds for connection
        'pool_size': 5,         # Maintain 5 connections
        'max_overflow': 0,      # No overflow connections for Cloud SQL
        'connect_args': {
            'charset': 'utf8mb4',
            'connect_timeout': 60,
            'read_timeout': 60,
            'write_timeout': 60,
            # Cloud SQL specific options
            'autocommit': True,
            'sql_mode': 'STRICT_TRANS_TABLES,NO_ZERO_DATE,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO'
        }
    }
    
    # Prevent automatic table drops - CRITICAL for Cloud SQL
    SQLALCHEMY_CREATE_ALL = True
    SQLALCHEMY_DROP_ALL = False
    
    # Cloud SQL Connection
    CLOUD_SQL_CONNECTION_NAME = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

    # Vertex AI Configuration (replaces Google AI)
    GOOGLE_CLOUD_PROJECT = os.environ.get('GOOGLE_CLOUD_PROJECT')
    GOOGLE_CLOUD_LOCATION = os.environ.get('GOOGLE_CLOUD_LOCATION', 'us-central1')
    GOOGLE_CLOUD_STAGING_BUCKET = os.environ.get('GOOGLE_CLOUD_STAGING_BUCKET')
    
    # Legacy Google AI support (for backward compatibility)
    GOOGLE_AI_API_KEY = os.environ.get('GOOGLE_AI_API_KEY')

    # Firebase
    FIREBASE_CREDENTIALS_PATH = os.environ.get('FIREBASE_CREDENTIALS_PATH')

    # Weather API (optional)
    WEATHER_API_KEY = os.environ.get('WEATHER_API_KEY')
    WEATHER_BASE_URL = os.environ.get('WEATHER_BASE_URL')