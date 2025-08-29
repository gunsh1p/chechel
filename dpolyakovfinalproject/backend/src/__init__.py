"""
Модуль для создания и настройки Flask-приложения сервиса бронирования мест
"""
from flask import Flask
from src.app.user_funcs import register_user, get_current_user_info
from flasgger import Swagger
from src.app.admin_funcs import list_all_users_admin, delete_user_admin
from src.app.booking_funcs import (create_booking, list_my_bookings,
                                   cancel_booking, move_booking)
from src.app.place_funcs import list_places, create_place, delete_place


def create_app():
    """
    Создает и конфигурирует экземпляр Flask-приложения.

    Настраивает Swagger, привязывает URL-маршруты и возвращает готовое приложение.
    """
    app = Flask(__name__)
    app.config['SWAGGER'] = {
        'title': 'CuWorking API',
        'openapi': '3.0.2'
    }
    swagger_template = {
        "openapi": "3.0.2",
        "info": {
            "title": "CuWorking API",
            "description": "API для сервиса CuWorking (бронирование мест в коворкинге)",
            "version": "1.0.1"
        },
        "paths": {},
        "components": {
            "schemas": {
                "Place": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "ID места", "readOnly": True},
                        "name": {"type": "string", "description": "Название места"},
                        "location": {"type": "string", "description": "Локация/зона"},
                        "description": {"type": "string", "description": "Описание места", "nullable": True},
                        "is_available": {"type": "boolean", "description": "Доступно ли место"}
                    },
                    "required": ["id", "name", "is_available"]
                },
                "User": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer", "description": "Уникальный идентификатор пользователя",
                               "readOnly": True},
                        "username": {"type": "string", "description": "Имя пользователя"},
                        "email": {"type": "string", "description": "Email пользователя"},
                        "is_admin": {"type": "boolean", "description": "Флаг администратора", "readOnly": True}
                    },
                    "required": ["id", "username", "email", "is_admin"]
                },
                "UserCreateRequest": {
                    "type": "object",
                    "properties": {
                        "username": {"type": "string", "description": "Имя пользователя"},
                        "email": {"type": "string", "description": "Email пользователя"},
                        "password": {"type": "string", "description": "Пароль"}
                    },
                    "required": ["username", "email", "password"]
                }
            },
            "responses": {
                "UnauthorizedError": {
                    "description": "Пользователь не авторизован",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "message": {"type": "string"}
                                }
                            },
                            "example": {"message": "Authentication required"}
                        }
                    }
                },
                "ForbiddenError": {
                    "description": "Доступ запрещён (требуется администратор)",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "message": {"type": "string"}
                                }
                            },
                            "example": {"message": "Administrator access required"}
                        }
                    }
                },
                "InternalServerError": {
                    "description": "Внутренняя ошибка сервера",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "error": {"type": "string"},
                                    "message": {"type": "string"}
                                }
                            },
                            "example": {"error": "Internal server error", "message": "..."}
                        }
                    }
                },
                "UserRegistered": {
                    "description": "Пользователь успешно зарегистрирован",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "message": {"type": "string"},
                                    "user_id": {"type": "integer"}
                                }
                            },
                            "example": {"message": "User registered successfully", "user_id": 1}
                        }
                    }
                },
                "MissingFieldsError": {
                    "description": "Не указаны обязательные поля",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "error": {"type": "string"}
                                }
                            },
                            "example": {"error": "Missing required fields (username, email, password)"}
                        }
                    }
                },
                "ConflictError": {
                    "description": "Пользователь с таким именем или email уже существует",
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "error": {"type": "string"}
                                }
                            },
                            "example": {"error": "Username or email already exists"}
                        }
                    }
                },
                "CurrentUserResponse": {
                    "description": "Информация о текущем пользователе",
                    "content": {
                        "application/json": {
                            "schema": {"$ref": "#/components/schemas/User"},
                            "example": {"id": 1, "username": "admin", "email": "admin@example.com", "is_admin": True}
                        }
                    }
                }
            }
        }
    }

    # Создаем все пути
    app.add_url_rule('/api/register', view_func=register_user, methods=['POST'])
    app.add_url_rule('/api/users/me', view_func=get_current_user_info, methods=['GET'])
    app.add_url_rule('/api/admin/users', view_func=list_all_users_admin, methods=['GET'])
    app.add_url_rule('/api/admin/users/<int:user_id>', view_func=delete_user_admin, methods=['DELETE'])
    app.add_url_rule('/api/bookings', view_func=create_booking, methods=['POST'])
    app.add_url_rule('/api/bookings', view_func=list_my_bookings, methods=['GET'])
    app.add_url_rule('/api/bookings/<int:booking_id>/cancel', view_func=cancel_booking, methods=['POST'])
    app.add_url_rule('/api/bookings/<int:booking_id>/move', view_func=move_booking, methods=['POST'])
    app.add_url_rule('/api/places', view_func=list_places, methods=['GET'])
    app.add_url_rule('/api/places', view_func=create_place, methods=['POST'])
    app.add_url_rule('/api/admin/places/<int:place_id>', view_func=delete_place, methods=['DELETE'])

    @app.route('/')
    def index():
        return "Backend is running!"

    Swagger(app, template=swagger_template)

    return app
