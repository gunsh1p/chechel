"""
Base model configuration for the BookCrossing application.

This module contains the SQLAlchemy database instance and base configuration
shared across all models.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()