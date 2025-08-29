"""
Authentication and authorization decorators for the BookCrossing application.

This module provides decorators for handling user authentication,
authorization, and request validation.
"""

from functools import wraps
from flask import jsonify, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
from app.models import User


def jwt_required_custom(f):
    """
    Custom JWT required decorator that verifies token and loads user.
    
    This decorator ensures that:
    1. A valid JWT token is present in the request
    2. The user associated with the token exists in the database
    3. The current user is available in the decorated function
    
    Args:
        f: The function to be decorated
        
    Returns:
        The decorated function with authentication checks
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            # Check if Authorization header is present
            from flask import request
            auth_header = request.headers.get('Authorization')
            if not auth_header:
                return jsonify({'error': 'Authorization header missing'}), 401
            
            if not auth_header.startswith('Bearer '):
                return jsonify({'error': 'Invalid authorization format. Use: Bearer <token>'}), 401
            
            verify_jwt_in_request()
            current_user_id_str = get_jwt_identity()
            
            if not current_user_id_str:
                return jsonify({'error': 'Invalid token - no user identity'}), 401
            
            # Convert string ID back to integer
            try:
                current_user_id = int(current_user_id_str)
            except (ValueError, TypeError):
                return jsonify({'error': 'Invalid user ID in token'}), 401
                
            current_user = User.query.get(current_user_id)
            
            if not current_user:
                return jsonify({'error': f'User not found with ID: {current_user_id}'}), 401
                
            return f(*args, current_user=current_user, **kwargs)
        except Exception as e:
            # Log the actual error for debugging
            import traceback
            print(f"JWT Auth Error: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            return jsonify({'error': f'Authentication failed: {str(e)}'}), 401
    
    return decorated_function


def admin_required(f):
    """
    Decorator that requires admin privileges to access the endpoint.
    
    This decorator should be used in combination with jwt_required_custom
    and ensures that only admin users can access the decorated endpoint.
    
    Args:
        f: The function to be decorated (must accept current_user as first argument)
        
    Returns:
        The decorated function with admin authorization checks
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = kwargs.pop('current_user')
        if not current_user.is_admin():
            return jsonify({'error': 'Admin privileges required'}), 403
        
        return f(*args, current_user=current_user, **kwargs)
    
    return decorated_function


def validate_request_data(required_fields, optional_fields=None):
    """
    Decorator to validate JSON request data for required and optional fields.
    
    Args:
        required_fields: List of field names that must be present
        optional_fields: List of field names that are optional
        
    Returns:
        Decorator function that validates request data
    """
    # Handle optional_fields default at decorator definition time
    if optional_fields is None:
        optional_fields = []
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Request must be JSON'}), 400
            
            data = request.get_json()
            
            # Check required fields
            for field in required_fields:
                if field not in data or data[field] is None or data[field] == '':
                    return jsonify({'error': f'Missing required field: {field}'}), 400
            
            # Extract only required and optional fields
            allowed_fields = required_fields + optional_fields
            cleaned_data = {k: v for k, v in data.items() if k in allowed_fields}
            
            return f(cleaned_data, *args, **kwargs)
        
        return decorated_function
    return decorator


def validate_pagination_and_filters():
    """
    Combined decorator to validate pagination and filter parameters from query string.
    
    Validates 'limit', 'offset' parameters and extracts filter parameters.
    
    Returns:
        Decorator function that provides pagination and filter parameters
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Validate pagination parameters
                limit = request.args.get('limit', 10, type=int)
                offset = request.args.get('offset', 0, type=int)
                
                if limit < 1 or limit > 100:
                    return jsonify({'error': 'Limit must be between 1 and 100'}), 400
                
                if offset < 0:
                    return jsonify({'error': 'Offset must be non-negative'}), 400
                
                # Extract filter parameters
                filters = {}
                
                if 'title' in request.args and request.args['title']:
                    filters['title'] = request.args['title']
                
                if 'author' in request.args and request.args['author']:
                    filters['author'] = request.args['author']
                
                if 'genre' in request.args and request.args['genre']:
                    filters['genre'] = request.args['genre']
                
                if 'available_only' in request.args:
                    available_only = request.args['available_only'].lower()
                    if available_only in ['true', '1', 'yes']:
                        filters['available_only'] = True
                    elif available_only in ['false', '0', 'no']:
                        filters['available_only'] = False
                
                if 'publish_year' in request.args:
                    try:
                        filters['publish_year'] = int(request.args['publish_year'])
                    except ValueError:
                        return jsonify({'error': 'Invalid publish_year parameter'}), 400
                
                return f(limit, offset, filters, *args, **kwargs)
            except ValueError:
                return jsonify({'error': 'Invalid pagination parameters'}), 400
        
        return decorated_function
    return decorator


def validate_pagination_params():
    """
    Decorator to validate and extract pagination parameters from query string.
    
    Validates 'limit' and 'offset' parameters and sets defaults if not provided.
    
    Returns:
        Decorator function that provides pagination parameters
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                limit = request.args.get('limit', 10, type=int)
                offset = request.args.get('offset', 0, type=int)
                
                # Validate pagination parameters
                if limit < 1 or limit > 100:
                    return jsonify({'error': 'Limit must be between 1 and 100'}), 400
                
                if offset < 0:
                    return jsonify({'error': 'Offset must be non-negative'}), 400
                
                return f(limit, offset, *args, **kwargs)
            except ValueError:
                return jsonify({'error': 'Invalid pagination parameters'}), 400
        
        return decorated_function
    return decorator