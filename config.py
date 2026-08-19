import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'aquaverde-dev-key-2024'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-dev-key-2024'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///aquaverde.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    DEBUG = True
    PORT = 5000