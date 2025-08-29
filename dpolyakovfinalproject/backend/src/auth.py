"""
Модуль для реализации базовой аутентификации и авторизации
"""
import base64
from functools import wraps
from flask import request, jsonify, g
from werkzeug.security import generate_password_hash, check_password_hash
from src.database import get_db
from src.models.user import User


def hash_password(password):
    """
    Хэширования пароля с помощья Werkzeug.
    """
    return generate_password_hash(password)


def verify_password(s_hash, provided_password):
    """
    Проверяет совпадает ли хэш и полученный пароль.
    """
    return check_password_hash(s_hash, provided_password)


def authenticate_basic():
    """
    Извлекает и декодирует учетные данные базовой авторизации из заголовка запроса.
    Возвращает кортеж (username, password) или None, если заголовок отсутствует
    или некорректен.
    """
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None

    parts = auth_header.split()
    if parts[0].lower() != 'basic' or len(parts) != 2:
        return None

    try:
        decoded_bytes = base64.b64decode(parts[1])
        decoded_string = decoded_bytes.decode('utf-8')

        # Формат "username:password"
        username, password = decoded_string.split(':', 1)
        return username, password
    except Exception:
        return None


def login_required(f):
    """
    Декоратор для защиты эндпоинтов, требующих авторизации.
    Извлекает учетные данные из заголовка Basic Auth, ищет пользователя
    в базе данных и проверяет пароль.
    Если авторизация успешна, сохраняет объект пользователя в g.current_user
    и вызывает декоратор.
    В противном случае возвращает ответ 401 Unauthorized.
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        info = authenticate_basic()
        if not info:
            return jsonify({"message": "Authentication required"}), 401

        username, password = info
        db_generator = get_db()
        db = next(db_generator)

        try:
            user = db.query(User).filter_by(username=username).first()

            if user is None or not verify_password(user.hashed_password, password):
                return jsonify({"message": "Invalid credentials"}), 401

            # Сохраняем пользователя в контекст запроса
            g.current_user = user

        except Exception as e:
            return jsonify({"error": "Authentication failed", "message": str(e)}), 500
        finally:
            db_generator.close()

        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """
    Декоратор для защиты эндпоинтов, требующих авторизации админа.
    Использует login_required, а затем проверяет, является ли пользователь админа.
    """

    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        # После login_required, пользователь находится в g.current_user, поэтому проверяем так
        if not hasattr(g, 'current_user') or not g.current_user.is_admin:
            return jsonify({"message": "Administrator access required"}), 403

        return f(*args, **kwargs)

    return decorated_function
