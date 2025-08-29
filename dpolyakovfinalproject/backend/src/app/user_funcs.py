"""
Модуль с методами для пользователей
"""
from flask import request, jsonify, g
from src.database import get_db
from src.models.user import User
from src.auth import login_required, hash_password
from sqlalchemy.exc import SQLAlchemyError


def register_user():
    """
    Регистрация нового пользователя.
    ---
    tags:
      - Users
    summary: Регистрация нового пользователя
    requestBody:
      required: true
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/UserCreateRequest'
    responses:
      201:
        $ref: '#/components/responses/UserRegistered'
      400:
        $ref: '#/components/responses/MissingFieldsError'
      409:
        $ref: '#/components/responses/ConflictError'
      500:
        $ref: '#/components/responses/InternalServerError'
    """
    data = request.get_json()
    if not data or not all(k in data for k in ('username', 'email', 'password')):
        return jsonify({"error": "Missing required fields (username, email, password)"}), 400
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    hashed_password = hash_password(password)
    db_generator = get_db()
    db = next(db_generator)

    try:
        # Пытаемся найти пользователя с такими же данными при регистрации
        existing_user = db.query(User).filter((User.username == username) | (User.email == email)).first()
        if existing_user:
            return jsonify({"error": "Username or email already exists"}), 409
        new_user = User(username=username, email=email, hashed_password=hashed_password, is_admin=False)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return jsonify({"message": "User registered successfully", "user_id": new_user.id}), 201
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({"error": "Database error", "message": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500
    finally:
        db_generator.close()


@login_required
def get_current_user_info():
    """
    Получить информацию о текущем аутентифицированном пользователе.
    ---
    tags:
      - Users
    summary: Получить информацию о текущем аутентифицированном пользователе
    security:
      - basicAuth: []
    responses:
      200:
        $ref: '#/components/responses/CurrentUserResponse'
      401:
        $ref: '#/components/responses/UnauthorizedError'
      500:
        $ref: '#/components/responses/InternalServerError'
    """
    user = g.current_user   # помним, что в g. лежит пользователь после авторизации
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_admin": user.is_admin
    }
    return jsonify(user_data), 200
