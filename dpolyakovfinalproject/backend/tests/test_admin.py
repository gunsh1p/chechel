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


def test_list_all_users_admin(client, basic_auth_headers):
    # Только админ может получить список
    resp = client.get('/api/admin/users', headers=basic_auth_headers('admin', 'admin123'))
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert any(u['username'] == 'admin' for u in data)


def test_list_all_users_forbidden(client, basic_auth_headers):
    # Регистрация
    client.post('/api/register', json={
        'username': 'user5', 'email': 'user5@example.com', 'password': 'pass5'})
    resp = client.get('/api/admin/users', headers=basic_auth_headers('user5', 'pass5'))
    assert resp.status_code == 403


def test_delete_user_admin(client, basic_auth_headers):
    # Регистрация
    client.post('/api/register', json={
        'username': 'user6', 'email': 'user6@example.com', 'password': 'pass6'})
    # Получить id пользователя
    resp = client.get('/api/admin/users', headers=basic_auth_headers('admin', 'admin123'))
    users = resp.get_json()
    user = next(u for u in users if u['username'] == 'user6')
    user_id = user['id']
    # Удалить пользователя
    resp = client.delete(f'/api/admin/users/{user_id}', headers=basic_auth_headers('admin', 'admin123'))
    assert resp.status_code == 200
    # Проверить, что он и вправду удалился
    resp = client.get('/api/admin/users', headers=basic_auth_headers('admin', 'admin123'))
    users = resp.get_json()
    assert not any(u['username'] == 'user6' for u in users)


def test_delete_user_forbidden(client, basic_auth_headers):
    # Регистрация
    client.post('/api/register', json={
        'username': 'user7', 'email': 'user7@example.com', 'password': 'pass7'})
    # Получить id пользователя
    resp = client.get('/api/admin/users', headers=basic_auth_headers('admin', 'admin123'))
    users = resp.get_json()
    user = next(u for u in users if u['username'] == 'user7')
    user_id = user['id']
    # Пользователь не может удалить
    resp = client.delete(f'/api/admin/users/{user_id}', headers=basic_auth_headers('user7', 'pass7'))
    assert resp.status_code == 403
