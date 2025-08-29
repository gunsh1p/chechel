"""
Configuration settings for the BookCrossing application.

This module contains configuration classes for different environments,
including database settings, JWT configuration, and application settings.
"""

import os
from datetime import timedelta


class Config:
    """
    Base configuration class containing common settings.
    
    Attributes:
        SECRET_KEY: Secret key for Flask sessions and JWT tokens
        JWT_SECRET_KEY: Separate JWT secret key
        JWT_ACCESS_TOKEN_EXPIRES: JWT token expiration time
        JWT_ALGORITHM: Algorithm used for JWT encoding/decoding
        SQLALCHEMY_TRACK_MODIFICATIONS: SQLAlchemy modification tracking
    """
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or SECRET_KEY
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
    JWT_ALGORITHM = 'HS256'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(Config):
    """
    Development environment configuration.
    
    Uses PostgreSQL database with development-specific settings.
    """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:password@localhost:5432/bookcrossing_dev'


class TestingConfig(Config):
    """
    Testing environment configuration.
    
    Uses separate test database and enables testing mode.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'postgresql://postgres:password@localhost:5432/bookcrossing_test'


class ProductionConfig(Config):
    """
    Production environment configuration.
    
    Uses production database with enhanced security settings.
    """
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:password@localhost:5432/bookcrossing_prod'


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}