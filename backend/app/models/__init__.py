"""
Database models package for the BookCrossing application.
"""

from .user import User, UserRole
from .book import Book

__all__ = ['User', 'UserRole', 'Book']