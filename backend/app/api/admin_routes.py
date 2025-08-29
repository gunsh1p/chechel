"""
Admin API routes for the BookCrossing application.

This module contains all admin-specific endpoints including user management,
role changes, and statistics.
"""

from flask import Blueprint, jsonify
from sqlalchemy import func
from datetime import datetime
from app.models import User, Book, UserRole
from app.models.base import db
from app.auth import jwt_required_custom, admin_required, validate_request_data, validate_pagination_params

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


@admin_bp.route('/users', methods=['GET'])
@jwt_required_custom
@admin_required
@validate_pagination_params()
def get_all_users(limit, offset, current_user):
    """
    Get all users (admin only).
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - in: query
        name: limit
        type: integer
        description: Number of users to return (1-100)
        default: 10
      - in: query
        name: offset
        type: integer
        description: Number of users to skip
        default: 0
    responses:
      200:
        description: List of users
      403:
        description: Admin privileges required
    """
    total = User.query.count()
    users = User.query.order_by(User.created_at.desc()).offset(offset).limit(limit).all()
    
    return jsonify({
        'users': [user.to_dict(include_sensitive=True) for user in users],
        'total': total
    }), 200


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required_custom
@admin_required
def delete_user(current_user, user_id):
    """
    Delete a user and their books (admin only).
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: User ID
    responses:
      200:
        description: User deleted successfully
      400:
        description: Cannot delete yourself
      403:
        description: Admin privileges required
      404:
        description: User not found
    """
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot delete yourself'}), 400
    
    user = User.query.get_or_404(user_id)
    
    try:
        # Delete user (books will be deleted due to cascade)
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete user'}), 500


@admin_bp.route('/users/<int:user_id>/role', methods=['PUT'])
@jwt_required_custom
@admin_required
@validate_request_data(['role'])
def change_user_role(data, current_user, user_id):
    """
    Change a user's role (admin only).
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    parameters:
      - in: path
        name: user_id
        type: integer
        required: true
        description: User ID
      - in: body
        name: role_data
        required: true
        schema:
          type: object
          required:
            - role
          properties:
            role:
              type: string
              enum: [user, admin]
              description: New role for the user
    responses:
      200:
        description: User role updated successfully
      400:
        description: Invalid role or cannot change your own role
      403:
        description: Admin privileges required
      404:
        description: User not found
    """
    if user_id == current_user.id:
        return jsonify({'error': 'Cannot change your own role'}), 400
    
    user = User.query.get_or_404(user_id)
    
    try:
        new_role = UserRole(data['role'])
    except ValueError:
        return jsonify({'error': 'Invalid role. Must be "user" or "admin"'}), 400
    
    try:
        user.role = new_role
        db.session.commit()
        
        return jsonify(user.to_dict(include_sensitive=True)), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to update user role'}), 500


@admin_bp.route('/statistics', methods=['GET'])
@jwt_required_custom
@admin_required
def get_statistics(current_user):
    """
    Get platform statistics (admin only).
    ---
    tags:
      - Admin
    security:
      - Bearer: []
    responses:
      200:
        description: Platform statistics
        schema:
          type: object
          properties:
            total_books:
              type: integer
            available_books:
              type: integer
            total_exchanges:
              type: integer
            total_users:
              type: integer
            most_popular_genre:
              type: string
            books_created_today:
              type: integer
      403:
        description: Admin privileges required
    """
    # Get basic counts
    total_books = Book.query.count()
    available_books = Book.query.filter(Book.taken_by.is_(None)).count()
    total_exchanges = Book.query.filter(Book.taken_by.isnot(None)).count()
    total_users = User.query.count()
    
    # Get most popular genre
    most_popular_genre_result = db.session.query(
        Book.genre, func.count(Book.genre).label('count')
    ).group_by(Book.genre).order_by(func.count(Book.genre).desc()).first()
    
    most_popular_genre = most_popular_genre_result.genre if most_popular_genre_result else 'N/A'
    
    # Get books created today
    today = datetime.utcnow().date()
    books_created_today = Book.query.filter(
        func.date(Book.created_at) == today
    ).count()
    
    return jsonify({
        'total_books': total_books,
        'available_books': available_books,
        'total_exchanges': total_exchanges,
        'total_users': total_users,
        'most_popular_genre': most_popular_genre,
        'books_created_today': books_created_today
    }), 200