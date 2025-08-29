import pytest
from src import create_app
from src.database import init_db
import base64
from datetime import datetime, timedelta


@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        init_db()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def get_auth_header(username, password):
    credentials = base64.b64encode(f'{username}:{password}'.encode()).decode()
    return {'Authorization': f'Basic {credentials}'}


def register_and_auth(client, username, email, password, basic_auth_headers):
    client.post('/api/register', json={
        'username': username, 'email': email, 'password': password
    })
    return basic_auth_headers(username, password)


def test_create_and_list_booking(client, basic_auth_headers):
    auth = register_and_auth(client, 'booker', 'booker@example.com', 'pass', basic_auth_headers)
    # Получить id места
    places = client.get('/api/places').get_json()
    place_id = places[0]['id']
    start = (datetime.now() + timedelta(days=1)).replace(microsecond=0, second=0)
    end = start + timedelta(hours=2)
    resp = client.post('/api/bookings', json={
        'place_id': place_id,
        'start_time': start.isoformat(),
        'end_time': end.isoformat()
    }, headers=auth)
    assert resp.status_code == 201
    # Бронирование появилось в списке
    resp = client.get('/api/bookings', headers=auth)
    assert resp.status_code == 200
    data = resp.get_json()
    assert any(b['place_id'] == place_id for b in data)


def test_booking_conflict(client, basic_auth_headers):
    auth = register_and_auth(client, 'booker2', 'booker2@example.com', 'pass', basic_auth_headers)
    places = client.get('/api/places').get_json()
    place_id = places[0]['id']
    start = (datetime.now() + timedelta(days=2)).replace(microsecond=0, second=0)
    end = start + timedelta(hours=2)
    # Первое бронирование
    client.post('/api/bookings', json={
        'place_id': place_id,
        'start_time': start.isoformat(),
        'end_time': end.isoformat()
    }, headers=auth)
    # Совпадающее бронирование
    resp = client.post('/api/bookings', json={
        'place_id': place_id,
        'start_time': (start + timedelta(minutes=30)).isoformat(),
        'end_time': (end + timedelta(minutes=30)).isoformat()
    }, headers=auth)
    assert resp.status_code == 409


def test_cancel_booking(client, basic_auth_headers):
    auth = register_and_auth(client, 'booker3', 'booker3@example.com', 'pass', basic_auth_headers)
    places = client.get('/api/places').get_json()
    place_id = places[0]['id']
    start = (datetime.now() + timedelta(days=3)).replace(microsecond=0, second=0)
    end = start + timedelta(hours=2)
    resp = client.post('/api/bookings', json={
        'place_id': place_id,
        'start_time': start.isoformat(),
        'end_time': end.isoformat()
    }, headers=auth)
    booking_id = resp.get_json()['id']
    # Отмена
    resp = client.post(f'/api/bookings/{booking_id}/cancel', headers=auth)
    assert resp.status_code == 200
    # Повторная отмена
    resp = client.post(f'/api/bookings/{booking_id}/cancel', headers=auth)
    assert resp.status_code == 400


def test_move_booking(client, basic_auth_headers):
    auth = register_and_auth(client, 'booker4', 'booker4@example.com', 'pass', basic_auth_headers)
    places = client.get('/api/places').get_json()
    place_id = places[0]['id']
    start = (datetime.now() + timedelta(days=4)).replace(microsecond=0, second=0)
    end = start + timedelta(hours=2)
    resp = client.post('/api/bookings', json={
        'place_id': place_id,
        'start_time': start.isoformat(),
        'end_time': end.isoformat()
    }, headers=auth)
    booking_id = resp.get_json()['id']
    # Перенос на другое время
    new_start = start + timedelta(hours=3)
    new_end = end + timedelta(hours=3)
    resp = client.post(f'/api/bookings/{booking_id}/move', json={
        'start_time': new_start.isoformat(),
        'end_time': new_end.isoformat()
    }, headers=auth)
    assert resp.status_code == 200
