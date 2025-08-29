"""
Authentication API routes for the BookCrossing application.

This module contains all authentication-related endpoints including
user registration, login, and logout.
"""

from flask import Blueprint, jsonify
from flask_jwt_extended import create_access_token
from app.models import User
from app.models.base import db
from app.auth import jwt_required_custom, validate_request_data

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')


@auth_bp.route('/register', methods=['POST'])
@validate_request_data(['username', 'password'])
def register(data):
    """
    Register a new user account.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: user
        description: User registration data
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              description: Unique username (max 255 characters)
              example: "john_doe"
            password:
              type: string
              description: User password
              example: "secure_password123"
    responses:
      201:
        description: User successfully registered
        schema:
          type: object
          properties:
            message:
              type: string
              example: "User registered successfully"
            user:
              type: object
              properties:
                id:
                  type: integer
                username:
                  type: string
                role:
                  type: string
      400:
        description: Invalid request data or username already exists
        schema:
          type: object
          properties:
            error:
              type: string
    """
    username = data['username'].strip()
    password = data['password']
    
    # Validate username length
    if len(username) > 255:
        return jsonify({'error': 'Username too long (max 255 characters)'}), 400
    
    # Check if username already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    # Create new user
    try:
        new_user = User(username, password)
        db.session.add(new_user)
        db.session.commit()
        
        return jsonify(new_user.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Registration failed'}), 500


@auth_bp.route('', methods=['POST'])
@validate_request_data(['username', 'password'])
def login(data):
    """
    Authenticate user and return JWT token.
    ---
    tags:
      - Authentication
    parameters:
      - in: body
        name: credentials
        description: User login credentials
        required: true
        schema:
          type: object
          required:
            - username
            - password
          properties:
            username:
              type: string
              description: Username
              example: "john_doe"
            password:
              type: string
              description: Password
              example: "secure_password123"
    responses:
      200:
        description: Login successful
        schema:
          type: object
          properties:
            access_token:
              type: string
              description: JWT access token
      401:
        description: Invalid credentials
        schema:
          type: object
          properties:
            error:
              type: string
    """
    username = data['username'].strip()
    password = data['password']
    
    user = User.query.filter_by(username=username).first()
    
    if user and user.check_password(password):
        access_token = create_access_token(identity=str(user.id))
        return jsonify({
            'access_token': access_token
        }), 200
    
    return jsonify({'error': 'Invalid credentials'}), 401


@auth_bp.route('/me', methods=['GET'])
@jwt_required_custom
def get_current_user(current_user):
    """
    Get current authenticated user information.
    ---
    tags:
      - Authentication
    security:
      - Bearer: []
    responses:
      200:
        description: Current user information
        schema:
          type: object
          properties:
            user:
              type: object
              properties:
                id:
                  type: integer
                username:
                  type: string
                role:
                  type: string
                created_at:
                  type: string
                  format: date-time
      401:
        description: Authentication required
        schema:
          type: object
          properties:
            error:
              type: string
    """
    return jsonify({'user': current_user.to_dict()}), 200


