"""
Tests for authentication endpoints in the BookCrossing application.

This module contains comprehensive tests for user registration, login, logout,
and authentication-related functionality.
"""

import pytest
import json
from app.models import User, UserRole


class TestUserRegistration:
    """Test cases for user registration endpoint."""
    
    def test_successful_registration(self, client, db_session):
        """
        Test successful user registration with valid data.
        
        Args:
            client: Test client fixture
            db_session: Database session fixture
        """
        response = client.post('/api/auth/register', json={
            'username': 'newuser',
            'password': 'newpassword123'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'User registered successfully'
        assert 'user' in data
        assert data['user']['username'] == 'newuser'
        assert data['user']['role'] == 'user'
        
        # Verify user was created in database
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.role == UserRole.USER
    
    def test_duplicate_username_registration(self, client, sample_user):
        """
        Test registration with duplicate username.
        
        Args:
            client: Test client fixture
            sample_user: Existing user fixture
        """
        response = client.post('/api/auth/register', json={
            'username': 'testuser',  # Same as sample_user
            'password': 'newpassword123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Username already exists' in data['error']
    
    def test_missing_username_registration(self, client):
        """
        Test registration with missing username.
        
        Args:
            client: Test client fixture
        """
        response = client.post('/api/auth/register', json={
            'password': 'newpassword123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Missing required field: username' in data['error']
    
    def test_missing_password_registration(self, client):
        """
        Test registration with missing password.
        
        Args:
            client: Test client fixture
        """
        response = client.post('/api/auth/register', json={
            'username': 'newuser'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Missing required field: password' in data['error']
    
    def test_empty_username_registration(self, client):
        """
        Test registration with empty username.
        
        Args:
            client: Test client fixture
        """
        response = client.post('/api/auth/register', json={
            'username': '',
            'password': 'newpassword123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Missing required field: username' in data['error']
    
    def test_long_username_registration(self, client):
        """
        Test registration with username exceeding maximum length.
        
        Args:
            client: Test client fixture
        """
        long_username = 'a' * 256  # Exceeds 255 character limit
        response = client.post('/api/auth/register', json={
            'username': long_username,
            'password': 'newpassword123'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Username too long' in data['error']
    
    def test_non_json_registration(self, client):
        """
        Test registration with non-JSON data.
        
        Args:
            client: Test client fixture
        """
        response = client.post('/api/auth/register', 
                             data='username=test&password=test',
                             content_type='application/x-www-form-urlencoded')
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Request must be JSON' in data['error']


class TestUserLogin:
    """Test cases for user login endpoint."""
    
    def test_successful_login(self, client, sample_user):
        """
        Test successful login with valid credentials.
        
        Args:
            client: Test client fixture
            sample_user: Sample user fixture
        """
        response = client.post('/api/auth', json={
            'username': 'testuser',
            'password': 'testpassword'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert 'user' in data
        assert data['user']['username'] == 'testuser'
        assert data['user']['role'] == 'user'
    
    def test_invalid_username_login(self, client):
        """
        Test login with invalid username.
        
        Args:
            client: Test client fixture
        """
        response = client.post('/api/auth', json={
            'username': 'nonexistentuser',
            'password': 'testpassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'Invalid credentials' in data['error']
    
    def test_invalid_password_login(self, client, sample_user):
        """
        Test login with invalid password.
        
        Args:
            client: Test client fixture
            sample_user: Sample user fixture
        """
        response = client.post('/api/auth', json={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'Invalid credentials' in data['error']
    
    def test_missing_credentials_login(self, client):
        """
        Test login with missing credentials.
        
        Args:
            client: Test client fixture
        """
        response = client.post('/api/auth', json={
            'username': 'testuser'
        })
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Missing required field: password' in data['error']
    
    def test_admin_login(self, client, sample_admin):
        """
        Test successful admin login.
        
        Args:
            client: Test client fixture
            sample_admin: Sample admin fixture
        """
        response = client.post('/api/auth', json={
            'username': 'testadmin',
            'password': 'adminpassword'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
        assert data['user']['role'] == 'admin'



class TestPasswordHashing:
    """Test cases for password hashing and verification."""
    
    def test_password_hashing(self, db_session):
        """
        Test that passwords are properly hashed.
        
        Args:
            db_session: Database session fixture
        """
        user = User('hashtest', 'plainpassword')
        db_session.add(user)
        db_session.commit()
        
        # Password should be hashed, not stored in plain text
        assert user.hashed_password != 'plainpassword'
        assert user.check_password('plainpassword') is True
        assert user.check_password('wrongpassword') is False
    
    def test_password_verification(self, sample_user):
        """
        Test password verification methods.
        
        Args:
            sample_user: Sample user fixture
        """
        assert sample_user.check_password('testpassword') is True
        assert sample_user.check_password('wrongpassword') is False
    
    def test_password_change(self, sample_user, db_session):
        """
        Test password change functionality.
        
        Args:
            sample_user: Sample user fixture
            db_session: Database session fixture
        """
        old_hash = sample_user.hashed_password
        sample_user.set_password('newpassword')
        
        # Hash should change
        assert sample_user.hashed_password != old_hash
        assert sample_user.check_password('newpassword') is True
        assert sample_user.check_password('testpassword') is False


class TestUserRoles:
    """Test cases for user role functionality."""
    
    def test_user_is_not_admin(self, sample_user):
        """
        Test that regular user is not admin.
        
        Args:
            sample_user: Sample user fixture
        """
        assert sample_user.is_admin() is False
    
    def test_admin_is_admin(self, sample_admin):
        """
        Test that admin user is admin.
        
        Args:
            sample_admin: Sample admin fixture
        """
        assert sample_admin.is_admin() is True
    
    def test_user_to_dict_basic(self, sample_user):
        """
        Test user to_dict method without sensitive info.
        
        Args:
            sample_user: Sample user fixture
        """
        user_dict = sample_user.to_dict()
        
        expected_keys = {'id', 'username', 'role', 'created_at'}
        assert set(user_dict.keys()) == expected_keys
        assert user_dict['username'] == 'testuser'
        assert user_dict['role'] == 'user'
    
    def test_user_to_dict_with_sensitive_info(self, sample_user):
        """
        Test user to_dict method with sensitive info.
        
        Args:
            sample_user: Sample user fixture
        """
        user_dict = sample_user.to_dict(include_sensitive=True)
        
        assert 'owned_books_count' in user_dict
        assert 'taken_books_count' in user_dict
        assert isinstance(user_dict['owned_books_count'], int)
        assert isinstance(user_dict['taken_books_count'], int)