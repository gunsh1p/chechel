"""
Book management API routes for the BookCrossing application.

This module contains all book-related endpoints including CRUD operations
and book taking functionality.
"""

from flask import Blueprint, jsonify
from datetime import datetime
from app.models import Book
from app.models.base import db
from app.auth import (
    jwt_required_custom, validate_request_data, validate_pagination_params,
    validate_pagination_and_filters, check_book_modification_rights, check_book_deletion_rights
)

books_bp = Blueprint('books', __name__, url_prefix='/api/books')


@books_bp.route('', methods=['GET'])
@jwt_required_custom
@validate_pagination_and_filters()
def get_books(limit, offset, filters, current_user):
    """
    Get books with pagination and optional filters.
    ---
    tags:
      - Books
    security:
      - Bearer: []
    parameters:
      - in: query
        name: limit
        type: integer
        description: Number of books to return (1-100)
        default: 10
      - in: query
        name: offset
        type: integer
        description: Number of books to skip
        default: 0
      - in: query
        name: title
        type: string
        description: Filter by book title (partial match)
      - in: query
        name: author
        type: string
        description: Filter by author name (partial match)
      - in: query
        name: genre
        type: string
        description: Filter by genre (partial match)
      - in: query
        name: available_only
        type: boolean
        description: Show only available books
      - in: query
        name: publish_year
        type: integer
        description: Filter by publication year
    responses:
      200:
        description: List of books
        schema:
          type: object
          properties:
            books:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  title:
                    type: string
                  author:
                    type: string
                  genre:
                    type: string
                  publish_year:
                    type: integer
                  is_available:
                    type: boolean
            total:
              type: integer
              description: Total number of books matching filters
            limit:
              type: integer
            offset:
              type: integer
    """
    query = Book.query
    
    # Apply filters
    if 'title' in filters:
        query = query.filter(Book.title.ilike(f"%{filters['title']}%"))
    
    if 'author' in filters:
        query = query.filter(Book.author.ilike(f"%{filters['author']}%"))
    
    if 'genre' in filters:
        query = query.filter(Book.genre.ilike(f"%{filters['genre']}%"))
    
    if 'publish_year' in filters:
        query = query.filter(Book.publish_year == filters['publish_year'])
    
    if filters.get('available_only'):
        query = query.filter(Book.taken_by.is_(None))
    
    # Get total count for pagination info
    total = query.count()
    
    # Apply pagination and get results
    books = query.order_by(Book.created_at.desc()).offset(offset).limit(limit).all()
    
    return jsonify({
        'books': [book.to_dict() for book in books],
        'total': total
    }), 200


@books_bp.route('/my', methods=['GET'])
@jwt_required_custom
@validate_pagination_params()
def get_my_books(limit, offset, current_user):
    """
    Get current user's posted books.
    ---
    tags:
      - Books
    security:
      - Bearer: []
    parameters:
      - in: query
        name: limit
        type: integer
        description: Number of books to return (1-100)
        default: 10
      - in: query
        name: offset
        type: integer
        description: Number of books to skip
        default: 0
    responses:
      200:
        description: List of user's books
        schema:
          type: object
          properties:
            books:
              type: array
              items:
                type: object
            total:
              type: integer
            limit:
              type: integer
            offset:
              type: integer
    """
    query = Book.query.filter_by(owner_id=current_user.id)
    total = query.count()
    
    books = query.order_by(Book.created_at.desc()).offset(offset).limit(limit).all()
    
    return jsonify({
        'books': [book.to_dict(include_owner_info=True) for book in books],
        'total': total
    }), 200


@books_bp.route('/taken', methods=['GET'])
@jwt_required_custom
@validate_pagination_params()
def get_taken_books(limit, offset, current_user):
    """
    Get books taken by current user.
    ---
    tags:
      - Books
    security:
      - Bearer: []
    parameters:
      - in: query
        name: limit
        type: integer
        description: Number of books to return (1-100)
        default: 10
      - in: query
        name: offset
        type: integer
        description: Number of books to skip
        default: 0
    responses:
      200:
        description: List of books taken by user
        schema:
          type: object
          properties:
            books:
              type: array
              items:
                type: object
            total:
              type: integer
            limit:
              type: integer
            offset:
              type: integer
    """
    query = Book.query.filter_by(taken_by=current_user.id)
    total = query.count()
    
    books = query.order_by(Book.created_at.desc()).offset(offset).limit(limit).all()
    
    return jsonify({
        'books': [book.to_dict(include_owner_info=True) for book in books],
        'total': total
    }), 200


@books_bp.route('', methods=['POST'])
@jwt_required_custom
@validate_request_data(['title', 'author', 'publish_year', 'genre', 'meeting_address'], 
                      ['description'])
def create_book(data, current_user):
    """
    Create a new book posting.
    ---
    tags:
      - Books
    security:
      - Bearer: []
    parameters:
      - in: body
        name: book
        description: Book data
        required: true
        schema:
          type: object
          required:
            - title
            - author
            - publish_year
            - genre
            - meeting_address
          properties:
            title:
              type: string
              description: Book title (max 255 characters)
              example: "The Great Gatsby"
            author:
              type: string
              description: Book author (max 255 characters)
              example: "F. Scott Fitzgerald"
            publish_year:
              type: integer
              description: Publication year
              example: 1925
            genre:
              type: string
              description: Book genre (max 255 characters)
              example: "Classic Literature"
            meeting_address:
              type: string
              description: Pickup address (max 255 characters)
              example: "123 Main St, City, State"
            description:
              type: string
              description: Optional book description (max 255 characters)
              example: "Great condition, minimal wear"
    responses:
      201:
        description: Book created successfully
        schema:
          type: object
          properties:
            message:
              type: string
            book:
              type: object
      400:
        description: Invalid request data
    """
    try:
        # Validate field lengths
        if len(data['title']) > 255:
            return jsonify({'error': 'Title too long (max 255 characters)'}), 400
        
        if len(data['author']) > 255:
            return jsonify({'error': 'Author too long (max 255 characters)'}), 400
        
        if len(data['genre']) > 255:
            return jsonify({'error': 'Genre too long (max 255 characters)'}), 400
        
        if len(data['meeting_address']) > 255:
            return jsonify({'error': 'Meeting address too long (max 255 characters)'}), 400
        
        if 'description' in data and data['description'] and len(data['description']) > 255:
            return jsonify({'error': 'Description too long (max 255 characters)'}), 400
        
        # Validate publish year
        if not isinstance(data['publish_year'], int) or data['publish_year'] < 0 or data['publish_year'] > datetime.now().year:
            return jsonify({'error': 'Invalid publish year'}), 400
        
        # Create book
        new_book = Book(
            owner_id=current_user.id,
            title=data['title'].strip(),
            author=data['author'].strip(),
            publish_year=data['publish_year'],
            genre=data['genre'].strip(),
            meeting_address=data['meeting_address'].strip(),
            description=data.get('description', '').strip() if data.get('description') else None
        )
        
        db.session.add(new_book)
        db.session.commit()
        
        return jsonify(new_book.to_dict(include_owner_info=True)), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to create book'}), 500


@books_bp.route('/<int:book_id>', methods=['PUT'])
@jwt_required_custom
@validate_request_data(['title', 'author', 'publish_year', 'genre', 'meeting_address'], 
                      ['description'])
def update_book(data, current_user, book_id):
    """
    Update a book posting.
    ---
    tags:
      - Books
    security:
      - Bearer: []
    parameters:
      - in: path
        name: book_id
        type: integer
        required: true
        description: Book ID
      - in: body
        name: book
        description: Updated book data
        required: true
        schema:
          type: object
          required:
            - title
            - author
            - publish_year
            - genre
            - meeting_address
          properties:
            title:
              type: string
            author:
              type: string
            publish_year:
              type: integer
            genre:
              type: string
            meeting_address:
              type: string
            description:
              type: string
    responses:
      200:
        description: Book updated successfully
      400:
        description: Invalid request data
      403:
        description: Cannot modify this book
      404:
        description: Book not found
    """
    book = Book.query.get_or_404(book_id)
    
    if not check_book_modification_rights(current_user, book):
        return jsonify({'error': 'Cannot modify this book (already taken or not owned by you)'}), 403
    
    try:
        # Validate and update book fields
        book.title = data['title'].strip()
        book.author = data['author'].strip()
        book.publish_year = data['publish_year']
        book.genre = data['genre'].strip()
        book.meeting_address = data['meeting_address'].strip()
        book.description = data.get('description', '').strip() if data.get('description') else None
        book.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify(book.to_dict(include_owner_info=True)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update book'}), 500


@books_bp.route('/<int:book_id>', methods=['DELETE'])
@jwt_required_custom
def delete_book(current_user, book_id):
    """
    Delete a book posting.
    ---
    tags:
      - Books
    security:
      - Bearer: []
    parameters:
      - in: path
        name: book_id
        type: integer
        required: true
        description: Book ID
    responses:
      200:
        description: Book deleted successfully
      403:
        description: Cannot delete this book
      404:
        description: Book not found
    """
    book = Book.query.get_or_404(book_id)
    
    if not check_book_deletion_rights(current_user, book):
        return jsonify({'error': 'Cannot delete this book'}), 403
    
    try:
        db.session.delete(book)
        db.session.commit()
        
        return jsonify({}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete book'}), 500


@books_bp.route('/<int:book_id>/take', methods=['POST'])
@jwt_required_custom
def take_book(current_user, book_id):
    """
    Take a book from another user.
    ---
    tags:
      - Books
    security:
      - Bearer: []
    parameters:
      - in: path
        name: book_id
        type: integer
        required: true
        description: Book ID
    responses:
      200:
        description: Book taken successfully
      400:
        description: Cannot take this book
      404:
        description: Book not found
    """
    book = Book.query.get_or_404(book_id)
    
    if not book.can_be_taken_by(current_user.id):
        return jsonify({'error': 'Cannot take this book (already taken, or it\'s your own book)'}), 400
    
    try:
        book.take_book(current_user.id)
        db.session.commit()
        
        return jsonify(book.to_dict(include_owner_info=True)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to take book'}), 500