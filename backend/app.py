"""
Main Flask application for the BookCrossing platform.

This module contains the Flask application factory and configuration
for the book sharing platform.
"""

from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flasgger import Swagger
import os

from config import config
from app.models.base import db
from app.models import User, UserRole
from app.api import auth_bp, books_bp, admin_bp


def create_app(config_name='default'):
    """
    Create and configure the Flask application.
    
    Args:
        config_name: Configuration environment name
        
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # Initialize extensions
    db.init_app(app)
    jwt = JWTManager(app)
    
    # Configure CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:3000", "http://127.0.0.1:3000"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Initialize Swagger
    swagger_config = {
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec_1",
                "route": "/openapi.json",
                "rule_filter": lambda rule: True,
                "model_filter": lambda tag: True,
            }
        ],
        "static_url_path": "/docs/static",
        "swagger_ui": True,
        "specs_route": "/docs/"
    }
    
    swagger_template = {
        "info": {
            "title": "BookCrossing API",
            "description": "API for a book sharing platform where users can post books for sharing and take books from others",
            "version": "1.0.0"
        },
        "securityDefinitions": {
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header",
                "description": "JWT authorization header using the Bearer scheme. Enter 'Bearer' [space] and then your token."
            }
        },
        "security": [{"Bearer": []}],
        "definitions": {
            "User": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "User ID"
                    },
                    "username": {
                        "type": "string",
                        "description": "Username"
                    },
                    "role": {
                        "type": "string",
                        "enum": ["user", "admin"],
                        "description": "User role"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Account creation timestamp"
                    }
                },
                "required": ["id", "username", "role", "created_at"]
            },
            "Book": {
                "type": "object",
                "properties": {
                    "id": {
                        "type": "integer",
                        "description": "Book ID"
                    },
                    "title": {
                        "type": "string",
                        "description": "Book title"
                    },
                    "author": {
                        "type": "string",
                        "description": "Book author"
                    },
                    "genre": {
                        "type": "string",
                        "description": "Book genre"
                    },
                    "publish_year": {
                        "type": "integer",
                        "description": "Publication year"
                    },
                    "description": {
                        "type": "string",
                        "description": "Book description"
                    },
                    "meeting_address": {
                        "type": "string",
                        "description": "Pickup/meeting address"
                    },
                    "is_available": {
                        "type": "boolean",
                        "description": "Whether book is available for taking"
                    },
                    "owner_id": {
                        "type": "integer",
                        "description": "ID of user who posted the book"
                    },
                    "taken_by": {
                        "type": "integer",
                        "description": "ID of user who took the book (null if available)"
                    },
                    "created_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Book posting timestamp"
                    },
                    "updated_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Last update timestamp"
                    },
                    "taken_at": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Timestamp when book was taken"
                    }
                },
                "required": ["id", "title", "author", "genre", "publish_year", "meeting_address", "is_available", "owner_id", "created_at"]
            },
            "BookList": {
                "type": "object",
                "properties": {
                    "books": {
                        "type": "array",
                        "items": {
                            "$ref": "#/definitions/Book"
                        },
                        "description": "List of books"
                    },
                    "total": {
                        "type": "integer",
                        "description": "Total number of books matching the criteria"
                    }
                },
                "required": ["books", "total"]
            },
            "UserList": {
                "type": "object",
                "properties": {
                    "users": {
                        "type": "array",
                        "items": {
                            "$ref": "#/definitions/User"
                        },
                        "description": "List of users"
                    },
                    "total": {
                        "type": "integer",
                        "description": "Total number of users"
                    }
                },
                "required": ["users", "total"]
            },
            "LoginRequest": {
                "type": "object",
                "properties": {
                    "username": {
                        "type": "string",
                        "description": "Username"
                    },
                    "password": {
                        "type": "string",
                        "description": "Password"
                    }
                },
                "required": ["username", "password"]
            },
            "LoginResponse": {
                "type": "object",
                "properties": {
                    "access_token": {
                        "type": "string",
                        "description": "JWT access token"
                    }
                },
                "required": ["access_token"]
            },
            "BookCreateRequest": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "maxLength": 255,
                        "description": "Book title"
                    },
                    "author": {
                        "type": "string",
                        "maxLength": 255,
                        "description": "Book author"
                    },
                    "genre": {
                        "type": "string",
                        "maxLength": 255,
                        "description": "Book genre"
                    },
                    "publish_year": {
                        "type": "integer",
                        "minimum": 0,
                        "description": "Publication year"
                    },
                    "description": {
                        "type": "string",
                        "maxLength": 255,
                        "description": "Book description"
                    },
                    "meeting_address": {
                        "type": "string",
                        "maxLength": 255,
                        "description": "Pickup/meeting address"
                    }
                },
                "required": ["title", "author", "genre", "publish_year", "meeting_address"]
            },
            "UserRoleUpdateRequest": {
                "type": "object",
                "properties": {
                    "role": {
                        "type": "string",
                        "enum": ["user", "admin"],
                        "description": "New user role"
                    }
                },
                "required": ["role"]
            },
            "Error": {
                "type": "object",
                "properties": {
                    "error": {
                        "type": "string",
                        "description": "Error message"
                    }
                },
                "required": ["error"]
            }
        }
    }
    
    swagger = Swagger(app, config=swagger_config, template=swagger_template)
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(books_bp)
    app.register_blueprint(admin_bp)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """
        Health check endpoint for monitoring and load balancers.
        ---
        tags:
          - Health
        responses:
          200:
            description: Application is healthy
            schema:
              type: object
              properties:
                status:
                  type: string
                  example: "healthy"
                timestamp:
                  type: string
                  example: "2025-08-29T09:52:00Z"
        """
        from datetime import datetime
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
    
    # Create database tables
    with app.app_context():
        db.create_all()
        
        # Create default admin user if it doesn't exist
        if not User.query.filter_by(username='admin').first():
            admin_user = User('admin', 'admin123', UserRole.ADMIN)
            db.session.add(admin_user)
            db.session.commit()
    
    # Error handling middleware
    @app.before_request
    def before_request():
        """Handle preflight requests and basic security headers."""
        from flask import request
        if request.method == 'OPTIONS':
            return '', 200
    
    @app.after_request
    def after_request(response):
        """Add security headers to all responses."""
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response
    
    # Error handlers
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({'error': 'Bad request'}), 400
    
    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({'error': 'Unauthorized'}), 401
    
    @app.errorhandler(403)
    def forbidden(error):
        return jsonify({'error': 'Forbidden'}), 403
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(422)
    def unprocessable_entity(error):
        return jsonify({'error': 'Unprocessable entity'}), 422
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        """Handle unexpected exceptions."""
        db.session.rollback()
        # Log the error in production
        app.logger.error(f'Unhandled exception: {str(error)}')
        return jsonify({'error': 'Internal server error'}), 500
    
    return app


if __name__ == '__main__':
    # Force production mode, disable debug
    app = create_app('production')
    app.run(host='0.0.0.0', port=5000, debug=False)