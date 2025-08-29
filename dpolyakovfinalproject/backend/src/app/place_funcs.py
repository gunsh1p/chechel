"""
Модуль с методами для управлениями местами
"""
from flask import request, jsonify
from src.database import get_db
from src.models.place import Place
from src.auth import login_required, admin_required
from sqlalchemy.exc import SQLAlchemyError


def list_places():
    """
    Получить список всех мест.
    ---
    tags:
      - Place
    summary: Получить список всех мест
    responses:
      200:
        description: Список всех мест.
        content:
          application/json:
            schema:
              type: array
              items:
                $ref: '#/components/schemas/Place'
      500:
        $ref: '#/components/responses/InternalServerError'
    """
    db_generator = get_db()
    db = next(db_generator)
    try:
        places = db.query(Place).all()
        result = []
        for p in places:
            result.append({
                'id': p.id,
                'name': p.name,
                'location': p.location,
                'description': p.description,
                'is_available': p.is_available
            })
        return jsonify(result), 200
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error', 'message': str(e)}), 500
    finally:
        db_generator.close()


@login_required
def create_place():
    """
    Добавить новое место (требуется авторизация).
    ---
    tags:
      - Place
    summary: Добавить новое место
    security:
      - basicAuth: []
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              name:
                type: string
                description: Название места
              location:
                type: string
                description: Локация/зона
              description:
                type: string
                description: Описание места
            required:
              - name
    responses:
      201:
        description: Место успешно добавлено.
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Place'
      400:
        description: Не указано название места.
      401:
        $ref: '#/components/responses/UnauthorizedError'
      500:
        $ref: '#/components/responses/InternalServerError'
    """
    data = request.get_json()
    name = data.get('name')
    location = data.get('location')
    description = data.get('description')
    is_available = data.get('is_available', True)
    if not name:
        return jsonify({'error': 'Название места обязательно'}), 400
    db_generator = get_db()
    db = next(db_generator)
    try:
        place = Place(
            name=name,
            location=location,
            description=description,
            is_available=is_available
        )
        db.add(place)
        db.commit()
        db.refresh(place)
        return jsonify(
            {'id': place.id, 'name': place.name, 'location': place.location, 'description': place.description,
             'is_available': place.is_available}), 201
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({'error': 'Database error', 'message': str(e)}), 500
    finally:
        db_generator.close()


@admin_required
def delete_place(place_id):
    """
    Удалить место по id (только для администратора).
    ---
    tags:
      - Place
    summary: Удалить место по id (только для администратора)
    security:
      - basicAuth: []
    parameters:
      - name: place_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Место удалено.
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
      401:
        $ref: '#/components/responses/UnauthorizedError'
      403:
        $ref: '#/components/responses/ForbiddenError'
      404:
        description: Место не найдено.
      500:
        $ref: '#/components/responses/InternalServerError'
    """
    db_generator = get_db()
    db = next(db_generator)
    try:
        place = db.query(Place).filter(Place.id == place_id).first()
        if not place:
            return jsonify({"error": "Место не найдено"}), 404
        db.delete(place)
        db.commit()
        return jsonify({"message": "Место удалено"}), 200
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({"error": "Database error", "message": str(e)}), 500
    finally:
        db_generator.close()
