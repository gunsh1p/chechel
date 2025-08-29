"""
API package for the BookCrossing application.
"""

from .auth_routes import auth_bp
from .book_routes import books_bp
from .admin_routes import admin_bp

__all__ = ['auth_bp', 'books_bp', 'admin_bp']