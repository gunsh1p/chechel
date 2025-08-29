"""
Book model for the BookCrossing application.

This module defines the Book model for managing books available for sharing.
"""

from datetime import datetime
from .base import db


class Book(db.Model):
    """
    Book model representing books available for sharing.
    
    Attributes:
        id: Primary key, unique identifier for the book
        owner_id: Foreign key to the user who owns/posted the book
        title: Book title (max 255 characters)
        description: Optional book description (max 255 characters)
        author: Book author (max 255 characters)
        publish_year: Year the book was published
        genre: Book genre (max 255 characters)
        meeting_address: Address where the book can be picked up (max 255 characters)
        taken_by: Foreign key to user who took the book (nullable)
        created_at: Timestamp when book was posted
        updated_at: Timestamp when book was last updated
    """
    
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False, index=True)
    description = db.Column(db.String(255), nullable=True)
    author = db.Column(db.String(255), nullable=False, index=True)
    publish_year = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(255), nullable=False, index=True)
    meeting_address = db.Column(db.String(255), nullable=False)
    taken_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, owner_id, title, author, publish_year, genre, meeting_address, description=None):
        """
        Initialize a new Book instance.
        
        Args:
            owner_id: ID of the user who owns the book
            title: Title of the book
            author: Author of the book
            publish_year: Year the book was published
            genre: Genre of the book
            meeting_address: Address where book can be picked up
            description: Optional description of the book
        """
        self.owner_id = owner_id
        self.title = title
        self.description = description
        self.author = author
        self.publish_year = publish_year
        self.genre = genre
        self.meeting_address = meeting_address
    
    def is_available(self):
        """
        Check if the book is available for taking.
        
        Returns:
            bool: True if book is available (not taken), False otherwise
        """
        return self.taken_by is None
    
    def can_be_modified_by(self, user_id):
        """
        Check if a user can modify this book.
        
        Args:
            user_id: ID of the user requesting modification
            
        Returns:
            bool: True if user can modify the book, False otherwise
        """
        return self.owner_id == user_id and self.is_available()
    
    def can_be_deleted_by(self, user_id, is_admin=False):
        """
        Check if a user can delete this book.
        
        Args:
            user_id: ID of the user requesting deletion
            is_admin: Whether the user is an admin
            
        Returns:
            bool: True if user can delete the book, False otherwise
        """
        if is_admin:
            return True
        return self.owner_id == user_id and self.is_available()
    
    def can_be_taken_by(self, user_id):
        """
        Check if a user can take this book.
        
        Args:
            user_id: ID of the user requesting to take the book
            
        Returns:
            bool: True if user can take the book, False otherwise
        """
        return self.is_available() and self.owner_id != user_id
    
    def take_book(self, user_id):
        """
        Mark the book as taken by a user.
        
        Args:
            user_id: ID of the user taking the book
            
        Returns:
            bool: True if book was successfully taken, False otherwise
        """
        if self.can_be_taken_by(user_id):
            self.taken_by = user_id
            self.updated_at = datetime.utcnow()
            return True
        return False
    
    def to_dict(self, include_owner_info=False):
        """
        Convert book instance to dictionary representation.
        
        Args:
            include_owner_info: Whether to include owner information
            
        Returns:
            dict: Dictionary representation of the book
        """
        result = {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'author': self.author,
            'publish_year': self.publish_year,
            'genre': self.genre,
            'meeting_address': self.meeting_address,
            'is_available': self.is_available(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
        
        if include_owner_info:
            result['owner_id'] = self.owner_id
            result['owner_username'] = self.owner.username if self.owner else None
            
        if self.taken_by:
            result['taken_by'] = self.taken_by
            result['taker_username'] = self.taker.username if self.taker else None
        
        return result
    
    def __repr__(self):
        return f'<Book {self.title} by {self.author}>'