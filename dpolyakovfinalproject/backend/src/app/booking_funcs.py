"""
Модуль с методами для бронирования мест
"""
from flask import request, jsonify, g
from src.database import get_db
from src.models.booking import Booking
from src.auth import login_required
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime


@login_required
def create_booking():
    """
    Создать новое бронирование рабочего места.
    ---
    tags:
      - Booking
    summary: Создать новое бронирование рабочего места
    security:
      - basicAuth: []
    responses:
      201:
        description: Бронирование успешно создано.
      400:
        description: Ошибка валидации данных.
      401:
        $ref: '#/components/responses/UnauthorizedError'
      403:
        $ref: '#/components/responses/ForbiddenError'
      409:
        description: Место уже забронировано на это время.
      500:
        $ref: '#/components/responses/InternalServerError'
    """
    data = request.get_json()
    user_id = g.current_user.id     # после авторизации тут лежит user
    place_id = data.get('place_id')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    if not (place_id and start_time and end_time):
        return jsonify({'error': 'Необходимо указать place_id, start_time, end_time'}), 400
    try:
        start_dt = datetime.fromisoformat(start_time)
        end_dt = datetime.fromisoformat(end_time)
    except Exception:
        return jsonify({'error': 'Неверный формат даты/времени'}), 400
    db_generator = get_db()
    db = next(db_generator)
    try:
        # проверяем нет ли брони на это время
        conflict = db.query(Booking).filter(
            Booking.place_id == place_id,
            Booking.status == 'active',
            Booking.end_time > start_dt,
            Booking.start_time < end_dt
        ).first()
        if conflict:
            return jsonify({'error': 'Место уже забронировано на это время'}), 409
        booking = Booking(
            user_id=user_id,
            place_id=place_id,
            start_time=start_dt,
            end_time=end_dt,
            status='active'
        )
        db.add(booking)
        db.commit()
        db.refresh(booking)
        return jsonify({
            'id': booking.id,
            'place_id': booking.place_id,
            'user_id': booking.user_id,
            'start_time': booking.start_time.isoformat(),
            'end_time': booking.end_time.isoformat(),
            'status': booking.status
        }), 201
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({'error': 'Database error', 'message': str(e)}), 500
    finally:
        db_generator.close()


@login_required
def list_my_bookings():
    """
    Получить список своих бронирований
    ---
    tags:
      - Booking
    summary: Получить список всех своих бронирований
    security:
      - basicAuth: []
    responses:
      200:
        description: Список всех бронирований пользователя.
        content:
          application/json:
            schema:
              type: array
              items:
                type: object
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
        bookings = db.query(Booking).filter(Booking.user_id == g.current_user.id).order_by(
            Booking.start_time.desc()).all()
        result = []
        for b in bookings:
            result.append({
                'id': b.id,
                'place_id': b.place_id,
                'start_time': b.start_time.isoformat(),
                'end_time': b.end_time.isoformat(),
                'status': b.status
            })
        return jsonify(result), 200
    except SQLAlchemyError as e:
        return jsonify({'error': 'Database error', 'message': str(e)}), 500
    finally:
        db_generator.close()


@login_required
def cancel_booking(booking_id):
    """
    Отменить своё бронирование
    ---
    tags:
      - Booking
    summary: Отменить своё бронирование
    security:
      - basicAuth: []
    responses:
      200:
        description: Бронирование отменено.
      400:
        description: Бронирование уже отменено или завершено.
      401:
        $ref: '#/components/responses/UnauthorizedError'
      403:
        $ref: '#/components/responses/ForbiddenError'
      404:
        description: Бронирование не найдено.
      500:
        $ref: '#/components/responses/InternalServerError'
    """
    db_generator = get_db()
    db = next(db_generator)
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id, Booking.user_id == g.current_user.id).first()
        if not booking:
            return jsonify({'error': 'Бронирование не найдено'}), 404
        if booking.status != 'active':
            return jsonify({'error': 'Бронирование уже отменено или завершено'}), 400
        booking.status = 'cancelled'
        db.add(booking)
        db.commit()
        return jsonify({'message': 'Бронирование отменено'}), 200
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({'error': 'Database error', 'message': str(e)}), 500
    finally:
        db_generator.close()


@login_required
def move_booking(booking_id):
    """
    Перенести своё бронирование (изменить время)
    ---
    tags:
      - Booking
    summary: Перенести своё бронирование (изменить время)
    security:
      - basicAuth: []
    responses:
      200:
        description: Бронирование перенесено.
      400:
        description: Неверный формат даты/времени или бронирование уже отменено/завершено.
      401:
        $ref: '#/components/responses/UnauthorizedError'
      403:
        $ref: '#/components/responses/ForbiddenError'
      404:
        description: Бронирование не найдено.
      409:
        description: Место уже забронировано на это время.
      500:
        $ref: '#/components/responses/InternalServerError'
    """
    data = request.get_json()
    db_generator = get_db()
    db = next(db_generator)
    try:
        booking = db.query(Booking).filter(Booking.id == booking_id, Booking.user_id == g.current_user.id).first()
        if not booking:
            return jsonify({'error': 'Бронирование не найдено'}), 404
        if booking.status != 'active':
            return jsonify({'error': 'Бронирование уже отменено или завершено'}), 400
        try:
            start_dt = datetime.fromisoformat(data.get('start_time'))
            end_dt = datetime.fromisoformat(data.get('end_time'))
        except Exception:
            return jsonify({'error': 'Неверный формат даты/времени'}), 400

        # Проверяем на наличие пересечений
        is_problem = db.query(Booking).filter(
            Booking.place_id == booking.place_id,
            Booking.status == 'active',
            Booking.id != booking.id,
            Booking.end_time > start_dt,
            Booking.start_time < end_dt
        ).first()
        if is_problem:
            return jsonify({'error': 'Место уже забронировано на это время'}), 409

        booking.start_time = start_dt
        booking.end_time = end_dt
        db.add(booking)
        db.commit()
        return jsonify({'message': 'Бронирование перенесено'}), 200
    except SQLAlchemyError as e:
        db.rollback()
        return jsonify({'error': 'Database error', 'message': str(e)}), 500
    finally:
        db_generator.close()
