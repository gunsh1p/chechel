"""
Tests for book management endpoints in the BookCrossing application.

This module contains comprehensive tests for book creation, reading, updating,
deletion, and book-taking functionality.
"""

import pytest
from datetime import datetime
from app.models import Book, User


class TestBookCreation:
    """Test cases for book creation endpoint."""
    
    def test_successful_book_creation(self, client, auth_headers, db_session):
        """
        Test successful book creation with valid data.
        
        Args:
            client: Test client fixture
            auth_headers: Authentication headers fixture
            db_session: Database session fixture
        """
        book_data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'publish_year': 2023,
            'genre': 'Fiction',
            'meeting_address': '123 Test Street',
            'description': 'A great test book'
        }
        
        response = client.post('/api/books', json=book_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['message'] == 'Book created successfully'
        assert 'book' in data
        assert data['book']['title'] == 'Test Book'
        assert data['book']['is_available'] is True
        
        # Verify book was created in database
        book = Book.query.filter_by(title='Test Book').first()
        assert book is not None
        assert book.author == 'Test Author'
    
    def test_book_creation_without_description(self, client, auth_headers):
        """
        Test book creation without optional description field.
        
        Args:
            client: Test client fixture
            auth_headers: Authentication headers fixture
        """
        book_data = {
            'title': 'Test Book No Desc',
            'author': 'Test Author',
            'publish_year': 2023,
            'genre': 'Fiction',
            'meeting_address': '123 Test Street'
        }
        
        response = client.post('/api/books', json=book_data, headers=auth_headers)
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['book']['description'] is None
    
    def test_book_creation_missing_required_field(self, client, auth_headers):
        """
        Test book creation with missing required field.
        
        Args:
            client: Test client fixture
            auth_headers: Authentication headers fixture
        """
        book_data = {
            'title': 'Test Book',
            'author': 'Test Author',
            # Missing publish_year
            'genre': 'Fiction',
            'meeting_address': '123 Test Street'
        }
        
        response = client.post('/api/books', json=book_data, headers=auth_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Missing required field: publish_year' in data['error']
    
    def test_book_creation_invalid_year(self, client, auth_headers):
        """
        Test book creation with invalid publication year.
        
        Args:
            client: Test client fixture
            auth_headers: Authentication headers fixture
        """
        book_data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'publish_year': 2050,  # Future year
            'genre': 'Fiction',
            'meeting_address': '123 Test Street'
        }
        
        response = client.post('/api/books', json=book_data, headers=auth_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid publish year' in data['error']
    
    def test_book_creation_without_auth(self, client):
        """
        Test book creation without authentication.
        
        Args:
            client: Test client fixture
        """
        book_data = {
            'title': 'Test Book',
            'author': 'Test Author',
            'publish_year': 2023,
            'genre': 'Fiction',
            'meeting_address': '123 Test Street'
        }
        
        response = client.post('/api/books', json=book_data)
        
        assert response.status_code == 401
    
    def test_book_creation_field_length_validation(self, client, auth_headers):
        """
        Test book creation with fields exceeding maximum length.
        
        Args:
            client: Test client fixture
            auth_headers: Authentication headers fixture
        """
        book_data = {
            'title': 'a' * 256,  # Exceeds 255 character limit
            'author': 'Test Author',
            'publish_year': 2023,
            'genre': 'Fiction',
            'meeting_address': '123 Test Street'
        }
        
        response = client.post('/api/books', json=book_data, headers=auth_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Title too long' in data['error']


class TestBookRetrieval:
    """Test cases for book retrieval endpoints."""
    
    def test_get_all_books(self, client, multiple_books):
        """
        Test retrieving all books with pagination.
        
        Args:
            client: Test client fixture
            multiple_books: Multiple books fixture
        """
        response = client.get('/api/books')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'books' in data
        assert 'total' in data
        assert 'limit' in data
        assert 'offset' in data
        assert len(data['books']) <= 10  # Default limit
        assert data['total'] == 5  # From multiple_books fixture
    
    def test_get_books_with_pagination(self, client, multiple_books):
        """
        Test book retrieval with custom pagination parameters.
        
        Args:
            client: Test client fixture
            multiple_books: Multiple books fixture
        """
        response = client.get('/api/books?limit=2&offset=1')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['books']) == 2
        assert data['limit'] == 2
        assert data['offset'] == 1
    
    def test_get_books_with_title_filter(self, client, multiple_books):
        """
        Test book retrieval with title filter.
        
        Args:
            client: Test client fixture
            multiple_books: Multiple books fixture
        """
        response = client.get('/api/books?title=Fiction')
        
        assert response.status_code == 200
        data = response.get_json()
        # Should return books with "Fiction" in title
        fiction_books = [book for book in data['books'] if 'Fiction' in book['title']]
        assert len(fiction_books) > 0
    
    def test_get_books_with_genre_filter(self, client, multiple_books):
        """
        Test book retrieval with genre filter.
        
        Args:
            client: Test client fixture
            multiple_books: Multiple books fixture
        """
        response = client.get('/api/books?genre=Fiction')
        
        assert response.status_code == 200
        data = response.get_json()
        # All returned books should be Fiction genre
        for book in data['books']:
            assert book['genre'] == 'Fiction'
    
    def test_get_books_available_only_filter(self, client, multiple_books, sample_user):
        """
        Test book retrieval with available_only filter.
        
        Args:
            client: Test client fixture
            multiple_books: Multiple books fixture
            sample_user: Sample user fixture
        """
        # Mark one book as taken
        book = multiple_books[0]
        book.taken_by = sample_user.id
        
        response = client.get('/api/books?available_only=true')
        
        assert response.status_code == 200
        data = response.get_json()
        # All returned books should be available
        for book in data['books']:
            assert book['is_available'] is True
    
    def test_get_books_invalid_pagination(self, client):
        """
        Test book retrieval with invalid pagination parameters.
        
        Args:
            client: Test client fixture
        """
        response = client.get('/api/books?limit=101')  # Exceeds maximum
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Limit must be between 1 and 100' in data['error']
    
    def test_get_my_books(self, client, auth_headers, sample_book):
        """
        Test retrieving current user's books.
        
        Args:
            client: Test client fixture
            auth_headers: Authentication headers fixture
            sample_book: Sample book fixture
        """
        response = client.get('/api/books/my', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'books' in data
        assert len(data['books']) >= 1
        # Check that returned books belong to the authenticated user
        for book in data['books']:
            assert 'owner_id' in book
    
    def test_get_my_books_without_auth(self, client):
        """
        Test retrieving user's books without authentication.
        
        Args:
            client: Test client fixture
        """
        response = client.get('/api/books/my')
        
        assert response.status_code == 401
    
    def test_get_taken_books(self, client, auth_headers):
        """
        Test retrieving books taken by current user.
        
        Args:
            client: Test client fixture
            auth_headers: Authentication headers fixture
        """
        response = client.get('/api/books/taken', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'books' in data
        assert 'total' in data


class TestBookUpdate:
    """Test cases for book update endpoint."""
    
    def test_successful_book_update(self, client, auth_headers, sample_book, db_session):
        """
        Test successful book update by owner.
        
        Args:
            client: Test client fixture
            auth_headers: Authentication headers fixture
            sample_book: Sample book fixture
            db_session: Database session fixture
        """
        update_data = {
            'title': 'Updated Test Book',
            'author': 'Updated Author',
            'publish_year': 2022,
            'genre': 'Updated Genre',
            'meeting_address': '456 Updated St',
            'description': 'Updated description'
        }
        
        response = client.put(f'/api/books/{sample_book.id}', 
                            json=update_data, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Book updated successfully'
        assert data['book']['title'] == 'Updated Test Book'
        
        # Verify update in database
        db_session.refresh(sample_book)
        assert sample_book.title == 'Updated Test Book'
    
    def test_update_nonexistent_book(self, client, auth_headers):
        """
        Test updating a non-existent book.
        
        Args:
            client: Test client fixture
            auth_headers: Authentication headers fixture
        """
        update_data = {
            'title': 'Updated Test Book',
            'author': 'Updated Author',
            'publish_year': 2022,
            'genre': 'Updated Genre',
            'meeting_address': '456 Updated St'
        }
        
        response = client.put('/api/books/999', json=update_data, headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_update_book_without_ownership(self, client, sample_book, db_session):
        """
        Test updating a book not owned by the user.
        
        Args:
            client: Test client fixture
            sample_book: Sample book fixture
            db_session: Database session fixture
        """
        # Create another user
        other_user = User('otheruser', 'otherpassword')
        db_session.add(other_user)
        db_session.commit()
        
        # Login as other user
        login_response = client.post('/api/auth', json={
            'username': 'otheruser',
            'password': 'otherpassword'
        })
        other_headers = {'Authorization': f'Bearer {login_response.get_json()["access_token"]}'}
        
        update_data = {
            'title': 'Unauthorized Update',
            'author': 'Unauthorized Author',
            'publish_year': 2022,
            'genre': 'Unauthorized',
            'meeting_address': '456 Unauthorized St'
        }
        
        response = client.put(f'/api/books/{sample_book.id}', 
                            json=update_data, headers=other_headers)
        
        assert response.status_code == 403
    
    def test_update_taken_book(self, client, auth_headers, sample_book, db_session):
        """
        Test updating a book that has been taken.
        
        Args:
            client: Test client fixture
            auth_headers: Authentication headers fixture
            sample_book: Sample book fixture
            db_session: Database session fixture
        """
        # Create another user and mark book as taken
        other_user = User('taker', 'takerpassword')
        db_session.add(other_user)
        db_session.commit()
        
        sample_book.taken_by = other_user.id
        db_session.commit()
        
        update_data = {
            'title': 'Updated Test Book',
            'author': 'Updated Author',
            'publish_year': 2022,
            'genre': 'Updated Genre',
            'meeting_address': '456 Updated St'
        }
        
        response = client.put(f'/api/books/{sample_book.id}', 
                            json=update_data, headers=auth_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'Cannot modify this book' in data['error']


class TestBookDeletion:
    """Test cases for book deletion endpoint."""
    
    def test_successful_book_deletion(self, client, auth_headers, sample_book):
        """
        Test successful book deletion by owner.
        
        Args:
            client: Test client fixture
            auth_headers: Authentication headers fixture
            sample_book: Sample book fixture
        """
        book_id = sample_book.id
        response = client.delete(f'/api/books/{book_id}', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Book deleted successfully'
        
        # Verify book was deleted
        assert Book.query.get(book_id) is None
    
    def test_delete_nonexistent_book(self, client, auth_headers):
        """
        Test deleting a non-existent book.
        
        Args:
            client: Test client fixture
            auth_headers: Authentication headers fixture
        """
        response = client.delete('/api/books/999', headers=auth_headers)
        
        assert response.status_code == 404
    
    def test_delete_book_without_ownership(self, client, sample_book, db_session):
        """
        Test deleting a book not owned by the user.
        
        Args:
            client: Test client fixture
            sample_book: Sample book fixture
            db_session: Database session fixture
        """
        # Create another user
        other_user = User('otheruser', 'otherpassword')
        db_session.add(other_user)
        db_session.commit()
        
        # Login as other user
        login_response = client.post('/api/auth', json={
            'username': 'otheruser',
            'password': 'otherpassword'
        })
        other_headers = {'Authorization': f'Bearer {login_response.get_json()["access_token"]}'}
        
        response = client.delete(f'/api/books/{sample_book.id}', headers=other_headers)
        
        assert response.status_code == 403


class TestBookTaking:
    """Test cases for book taking endpoint."""
    
    def test_successful_book_taking(self, client, sample_book, db_session):
        """
        Test successfully taking an available book.
        
        Args:
            client: Test client fixture
            sample_book: Sample book fixture
            db_session: Database session fixture
        """
        # Create another user to take the book
        taker = User('booktaker', 'takerpassword')
        db_session.add(taker)
        db_session.commit()
        
        # Login as taker
        login_response = client.post('/api/auth', json={
            'username': 'booktaker',
            'password': 'takerpassword'
        })
        taker_headers = {'Authorization': f'Bearer {login_response.get_json()["access_token"]}'}
        
        response = client.post(f'/api/books/{sample_book.id}/take', headers=taker_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Book taken successfully'
        assert data['book']['is_available'] is False
        
        # Verify in database
        db_session.refresh(sample_book)
        assert sample_book.taken_by == taker.id
    
    def test_take_own_book(self, client, auth_headers, sample_book):
        """
        Test attempting to take own book.
        
        Args:
            client: Test client fixture
            auth_headers: Authentication headers fixture
            sample_book: Sample book fixture
        """
        response = client.post(f'/api/books/{sample_book.id}/take', headers=auth_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Cannot take this book' in data['error']
    
    def test_take_already_taken_book(self, client, sample_book, db_session):
        """
        Test attempting to take an already taken book.
        
        Args:
            client: Test client fixture
            sample_book: Sample book fixture
            db_session: Database session fixture
        """
        # Create first taker
        first_taker = User('firsttaker', 'password1')
        db_session.add(first_taker)
        db_session.commit()
        
        # Mark book as taken
        sample_book.taken_by = first_taker.id
        db_session.commit()
        
        # Create second user trying to take the book
        second_taker = User('secondtaker', 'password2')
        db_session.add(second_taker)
        db_session.commit()
        
        # Login as second taker
        login_response = client.post('/api/auth', json={
            'username': 'secondtaker',
            'password': 'password2'
        })
        second_headers = {'Authorization': f'Bearer {login_response.get_json()["access_token"]}'}
        
        response = client.post(f'/api/books/{sample_book.id}/take', headers=second_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Cannot take this book' in data['error']
    
    def test_take_book_without_auth(self, client, sample_book):
        """
        Test taking a book without authentication.
        
        Args:
            client: Test client fixture
            sample_book: Sample book fixture
        """
        response = client.post(f'/api/books/{sample_book.id}/take')
        
        assert response.status_code == 401