def test_register_user_success(client):
    resp = client.post('/api/register', json={
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpass123'
    })
    assert resp.status_code == 201
    data = resp.get_json()
    assert 'user_id' in data
    assert data['message'] == 'User registered successfully'


def test_register_user_missing_fields(client):
    resp = client.post('/api/register', json={
        'username': 'testuser2'
    })
    assert resp.status_code == 400
    data = resp.get_json()
    assert 'error' in data


def test_register_user_conflict(client):
    # Регистрация
    client.post('/api/register', json={
        'username': 'testuser3',
        'email': 'testuser3@example.com',
        'password': 'testpass123'
    })
    # Регистрация с той же инфой
    resp = client.post('/api/register', json={
        'username': 'testuser3',
        'email': 'other@example.com',
        'password': 'testpass123'
    })
    assert resp.status_code == 409
    data = resp.get_json()
    assert 'error' in data


def test_get_current_user_info(client, basic_auth_headers):
    # Регистрация
    client.post('/api/register', json={
        'username': 'testuser4',
        'email': 'testuser4@example.com',
        'password': 'testpass123'
    })
    # Basic Auth
    headers = basic_auth_headers('testuser4', 'testpass123')
    resp = client.get('/api/users/me', headers=headers)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['username'] == 'testuser4'
    assert data['email'] == 'testuser4@example.com'
    assert data['is_admin'] is False
