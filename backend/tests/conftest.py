"""
Pytest configuration and fixtures for the BookCrossing application tests.

This module provides common fixtures and setup for testing the Flask application,
including database setup, test client creation, and sample data.
"""

import pytest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from testcontainers.postgres import PostgresContainer
from app import create_app
from app.models.base import db
from app.models import User, Book, UserRole


@pytest.fixture(scope='session')
def postgres_container():
    """
    Create a PostgreSQL test container for testing.
    
    Yields:
        PostgresContainer: Running PostgreSQL container instance
    """
    with PostgresContainer("postgres:13") as postgres:
        yield postgres


@pytest.fixture(scope='session')
def app_config(postgres_container):
    """
    Create application configuration for testing.
    
    Args:
        postgres_container: PostgreSQL container fixture
        
    Returns:
        dict: Configuration dictionary for the test application
    """
    return {
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': postgres_container.get_connection_url(),
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'JWT_ACCESS_TOKEN_EXPIRES': False,  # Tokens don't expire in tests
        'SECRET_KEY': 'test-secret-key'
    }


@pytest.fixture(scope='session')
def app(app_config):
    """
    Create Flask application instance for testing.
    
    Args:
        app_config: Application configuration fixture
        
    Returns:
        Flask: Configured Flask application for testing
    """
    app = create_app('testing')
    app.config.update(app_config)
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """
    Create test client for making HTTP requests.
    
    Args:
        app: Flask application fixture
        
    Returns:
        FlaskClient: Test client for the application
    """
    return app.test_client()


@pytest.fixture(scope='function')
def db_session(app):
    """
    Create database session for tests with automatic rollback.
    
    Args:
        app: Flask application fixture
        
    Yields:
        Session: SQLAlchemy session for database operations
    """
    with app.app_context():
        connection = db.engine.connect()
        transaction = connection.begin()
        
        # Configure session to use the connection
        session = db.create_scoped_session(
            options={"bind": connection, "binds": {}}
        )
        db.session = session
        
        yield session
        
        # Rollback transaction and close connection
        transaction.rollback()
        connection.close()
        session.remove()


@pytest.fixture
def sample_user(db_session):
    """
    Create a sample user for testing.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        User: Sample user instance
    """
    user = User('testuser', 'testpassword', UserRole.USER)
    db_session.add(user)
    db_session.commit()
    return user


@pytest.fixture
def sample_admin(db_session):
    """
    Create a sample admin user for testing.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        User: Sample admin user instance
    """
    admin = User('testadmin', 'adminpassword', UserRole.ADMIN)
    db_session.add(admin)
    db_session.commit()
    return admin


@pytest.fixture
def sample_book(db_session, sample_user):
    """
    Create a sample book for testing.
    
    Args:
        db_session: Database session fixture
        sample_user: Sample user fixture
        
    Returns:
        Book: Sample book instance
    """
    book = Book(
        owner_id=sample_user.id,
        title='Test Book',
        author='Test Author',
        publish_year=2023,
        genre='Fiction',
        meeting_address='123 Test St',
        description='A test book'
    )
    db_session.add(book)
    db_session.commit()
    return book


@pytest.fixture
def auth_headers(client, sample_user):
    """
    Create authorization headers for authenticated requests.
    
    Args:
        client: Test client fixture
        sample_user: Sample user fixture
        
    Returns:
        dict: Headers dictionary with JWT token
    """
    response = client.post('/api/auth', json={
        'username': 'testuser',
        'password': 'testpassword'
    })
    
    token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def admin_headers(client, sample_admin):
    """
    Create authorization headers for admin requests.
    
    Args:
        client: Test client fixture
        sample_admin: Sample admin fixture
        
    Returns:
        dict: Headers dictionary with admin JWT token
    """
    response = client.post('/api/auth', json={
        'username': 'testadmin',
        'password': 'adminpassword'
    })
    
    token = response.get_json()['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture
def multiple_books(db_session, sample_user):
    """
    Create multiple books for pagination and filtering tests.
    
    Args:
        db_session: Database session fixture
        sample_user: Sample user fixture
        
    Returns:
        list: List of book instances
    """
    books = []
    
    # Create books with different genres and years
    book_data = [
        {'title': 'Fiction Book 1', 'author': 'Author A', 'genre': 'Fiction', 'year': 2020},
        {'title': 'Science Book', 'author': 'Author B', 'genre': 'Science', 'year': 2021},
        {'title': 'Fiction Book 2', 'author': 'Author C', 'genre': 'Fiction', 'year': 2022},
        {'title': 'History Book', 'author': 'Author D', 'genre': 'History', 'year': 2023},
        {'title': 'Mystery Book', 'author': 'Author E', 'genre': 'Mystery', 'year': 2023}
    ]
    
    for data in book_data:
        book = Book(
            owner_id=sample_user.id,
            title=data['title'],
            author=data['author'],
            publish_year=data['year'],
            genre=data['genre'],
            meeting_address='123 Test St',
            description=f"Description for {data['title']}"
        )
        db_session.add(book)
        books.append(book)
    
    db_session.commit()
    return books