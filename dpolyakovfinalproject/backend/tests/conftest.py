import pytest
from testcontainers.postgres import PostgresContainer
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src import create_app
from src.database import Base
from src.models.user import User
from src.auth import hash_password
import base64


# Фикстура для запуска временного контейнера PostgreSQL
@pytest.fixture(scope='session')
def postgres_engine():
    with PostgresContainer("postgres:16") as postgres:
        engine = create_engine(postgres.get_connection_url())
        Base.metadata.create_all(engine)
        yield engine
        engine.dispose()


# Фикстура для создания новой сессии и чистой схемы
@pytest.fixture(scope='function')
def db_session(postgres_engine):
    Session = sessionmaker(bind=postgres_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


# Фикстура для Flask-приложения
@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config['TESTING'] = True
    yield app


# Фикстура для тестового клиента Flask
@pytest.fixture(scope="function")
def client(app):
    with app.test_client() as client:
        yield client


# Basic Auth
@pytest.fixture
def basic_auth_headers():
    def _headers(username, password):
        credentials = f"{username}:{password}"
        token = base64.b64encode(credentials.encode('utf-8')).decode('utf-8')
        return {'Authorization': f'Basic {token}'}

    return _headers


# Создание пользователя напрямую в БД
@pytest.fixture
def create_user(db_session):
    def _create_user(username, password, email, is_admin=False):
        user = User(
            username=username,
            email=email,
            hashed_password=hash_password(password),
            is_admin=is_admin
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return user

    return _create_user
