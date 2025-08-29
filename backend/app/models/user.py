"""
User model for the BookCrossing application.

This module defines the User model with authentication and authorization
functionality.
"""

from datetime import datetime
from enum import Enum
from werkzeug.security import generate_password_hash, check_password_hash
from .base import db


class UserRole(Enum):
    """
    Enumeration for user roles in the system.
    
    Values:
        USER: Regular user with basic permissions
        ADMIN: Administrator with elevated permissions
    """
    USER = 'user'
    ADMIN = 'admin'


class User(db.Model):
    """
    User model representing registered users in the system.
    
    Attributes:
        id: Primary key, unique identifier for the user
        username: Unique username for login (max 255 characters)
        hashed_password: Bcrypt hashed password (max 255 characters)
        role: User role (USER or ADMIN)
        created_at: Timestamp when user was created
        owned_books: Relationship to books owned by this user
        taken_books: Relationship to books taken by this user
    """
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), unique=True, nullable=False, index=True)
    hashed_password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.USER)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    owned_books = db.relationship('Book', foreign_keys='Book.owner_id', 
                                 backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    taken_books = db.relationship('Book', foreign_keys='Book.taken_by', 
                                 backref='taker', lazy='dynamic')
    
    def __init__(self, username, password, role=UserRole.USER):
        """
        Initialize a new User instance.
        
        Args:
            username: Unique username for the user
            password: Plain text password (will be hashed)
            role: User role (defaults to USER)
        """
        self.username = username
        self.set_password(password)
        self.role = role
    
    def set_password(self, password):
        """
        Hash and set the user's password.
        
        Args:
            password: Plain text password to hash and store
        """
        self.hashed_password = generate_password_hash(password)
    
    def check_password(self, password):
        """
        Verify a password against the stored hash.
        
        Args:
            password: Plain text password to verify
            
        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.hashed_password, password)
    
    def is_admin(self):
        """
        Check if the user has admin privileges.
        
        Returns:
            bool: True if user is an admin, False otherwise
        """
        return self.role == UserRole.ADMIN
    
    def to_dict(self, include_sensitive=False):
        """
        Convert user instance to dictionary representation.
        
        Args:
            include_sensitive: Whether to include sensitive information
            
        Returns:
            dict: Dictionary representation of the user
        """
        result = {
            'id': self.id,
            'username': self.username,
            'role': self.role.value,
            'created_at': self.created_at.isoformat()
        }
        
        if include_sensitive:
            result['owned_books_count'] = self.owned_books.count()
            result['taken_books_count'] = self.taken_books.count()
        
        return result
    
    def __repr__(self):
        return f'<User {self.username}>'