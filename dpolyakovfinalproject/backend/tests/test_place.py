import pytest
from src import create_app
from src.database import init_db
import base64


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


def test_list_places(client):
    resp = client.get('/api/places')
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert 'name' in data[0]


def test_create_place_requires_auth(client):
    resp = client.post('/api/places', json={
        'name': 'Test Place',
        'location': 'Test Location',
        'description': 'Test Desc'
    })
    assert resp.status_code == 401


def test_create_place_success(client, basic_auth_headers):
    # Регистрация
    client.post('/api/register', json={
        'username': 'user1', 'email': 'user1@example.com', 'password': 'pass1'})
    resp = client.post('/api/places', json={
        'name': 'Test Place 2',
        'location': 'Test Location',
        'description': 'Test Desc'
    }, headers=basic_auth_headers('user1', 'pass1'))
    assert resp.status_code == 201
    data = resp.get_json()
    assert data['name'] == 'Test Place 2'


def test_delete_place_admin_only(client, basic_auth_headers):
    # Регистрация
    client.post('/api/register', json={
        'username': 'user2', 'email': 'user2@example.com', 'password': 'pass2'})

    resp = client.delete('/api/admin/places/1', headers=basic_auth_headers('user2', 'pass2'))
    assert resp.status_code == 403

    resp = client.delete('/api/admin/places/1', headers=basic_auth_headers('admin', 'admin123'))
    assert resp.status_code in (200, 404)  # Может быть 404, если тестовое место уже удалено
