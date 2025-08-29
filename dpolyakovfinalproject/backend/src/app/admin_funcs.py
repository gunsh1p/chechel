"""
Модуль с методами для администратора
"""
from flask import jsonify
from src.database import get_db
from src.models.user import User
from src.auth import admin_required
from sqlalchemy.exc import SQLAlchemyError


@admin_required
def list_all_users_admin():
    """
    Получить список всех пользователей в системе.
    ---
    tags:
      - Admin
    summary: Получить список всех пользователей в системе (администратор)
    security:
      - basicAuth: []
    responses:
      200:
        description: Список всех пользователей.
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/User'
      401:
        $ref: '#/components/responses/UnauthorizedError'
      403:
        $ref: '#/components/responses/ForbiddenError'
      500:
        $ref: '#/components/responses/InternalServerError'
    """
    db_generator = get_db()     # создали генератор, который управляет сессией
    db = next(db_generator)     # получили саму сессию
    try:
        users = db.query(User).order_by(User.id).all()
        users_list = []
        for user in users:
            users_list.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_admin": user.is_admin
            })
        return jsonify(users_list), 200
    except SQLAlchemyError as e:
        return jsonify({"error": "Database error", "message": str(e)}), 500
    except Exception as e:
        return jsonify({"error": "Internal server error", "message": str(e)}), 500
    finally:
        db_generator.close()


@admin_required
def delete_user_admin(user_id):
    """
    Удалить пользователя по id (только для администратора).
    ---
    tags:
      - Admin
    summary: Удалить пользователя по id (администратор)
    security:
      - basicAuth: []
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Пользователь успешно удалён.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      404:
        description: Пользователь не найден.
      401:
        $ref: '#/components/responses/UnauthorizedError'
      403:
        $ref: '#/components/responses/ForbiddenError'
      500:
        $ref: '#/components/responses/InternalServerError'
    """
    db_generator = get_db()
    db = next(db_generator)
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return jsonify({"message": "User not found"}), 404
        db.delete(user)
        db.commit()
        return jsonify({"message": "User deleted by admin"}), 200
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({"error": "Database error", "message": str(e)}), 500
    finally:
        db_generator.close()
