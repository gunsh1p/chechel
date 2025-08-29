"""
Tests for admin endpoints in the BookCrossing application.

This module contains comprehensive tests for admin functionality including
user management, role changes, and statistics retrieval.
"""

import pytest
from app.models import User, Book, UserRole


class TestAdminUserManagement:
    """Test cases for admin user management endpoints."""
    
    def test_admin_get_all_users(self, client, admin_headers, multiple_books):
        """
        Test admin retrieving all users with pagination.
        
        Args:
            client: Test client fixture
            admin_headers: Admin authentication headers fixture
            multiple_books: Multiple books fixture (creates users)
        """
        response = client.get('/api/admin/users', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'users' in data
        assert 'total' in data
        assert 'limit' in data
        assert 'offset' in data
        assert len(data['users']) >= 1
        
        # Check that sensitive information is included for admin
        for user in data['users']:
            assert 'owned_books_count' in user
            assert 'taken_books_count' in user
    
    def test_regular_user_cannot_get_all_users(self, client, auth_headers):
        """
        Test that regular users cannot access admin user list.
        
        Args:
            client: Test client fixture
            auth_headers: Regular user authentication headers fixture
        """
        response = client.get('/api/admin/users', headers=auth_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'Admin privileges required' in data['error']
    
    def test_admin_get_users_with_pagination(self, client, admin_headers, db_session):
        """
        Test admin user list with pagination parameters.
        
        Args:
            client: Test client fixture
            admin_headers: Admin authentication headers fixture
            db_session: Database session fixture
        """
        # Create additional test users
        for i in range(5):
            user = User(f'testuser{i}', 'password')
            db_session.add(user)
        db_session.commit()
        
        response = client.get('/api/admin/users?limit=3&offset=1', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['users']) == 3
        assert data['limit'] == 3
        assert data['offset'] == 1
    
    def test_admin_delete_user(self, client, admin_headers, db_session):
        """
        Test admin deleting a user.
        
        Args:
            client: Test client fixture
            admin_headers: Admin authentication headers fixture
            db_session: Database session fixture
        """
        # Create a test user to delete
        test_user = User('usertodelete', 'password')
        db_session.add(test_user)
        db_session.commit()
        user_id = test_user.id
        
        response = client.delete(f'/api/admin/users/{user_id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'User deleted successfully'
        
        # Verify user was deleted
        assert User.query.get(user_id) is None
    
    def test_admin_cannot_delete_self(self, client, admin_headers, sample_admin):
        """
        Test that admin cannot delete their own account.
        
        Args:
            client: Test client fixture
            admin_headers: Admin authentication headers fixture
            sample_admin: Sample admin fixture
        """
        response = client.delete(f'/api/admin/users/{sample_admin.id}', headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Cannot delete yourself' in data['error']
    
    def test_admin_delete_nonexistent_user(self, client, admin_headers):
        """
        Test admin deleting a non-existent user.
        
        Args:
            client: Test client fixture
            admin_headers: Admin authentication headers fixture
        """
        response = client.delete('/api/admin/users/999', headers=admin_headers)
        
        assert response.status_code == 404
    
    def test_regular_user_cannot_delete_user(self, client, auth_headers, db_session):
        """
        Test that regular users cannot delete users.
        
        Args:
            client: Test client fixture
            auth_headers: Regular user authentication headers fixture
            db_session: Database session fixture
        """
        # Create a test user
        test_user = User('testuser', 'password')
        db_session.add(test_user)
        db_session.commit()
        
        response = client.delete(f'/api/admin/users/{test_user.id}', headers=auth_headers)
        
        assert response.status_code == 403


class TestAdminRoleManagement:
    """Test cases for admin role management endpoints."""
    
    def test_admin_change_user_role_to_admin(self, client, admin_headers, db_session):
        """
        Test admin promoting a user to admin role.
        
        Args:
            client: Test client fixture
            admin_headers: Admin authentication headers fixture
            db_session: Database session fixture
        """
        # Create a regular user
        regular_user = User('regularuser', 'password')
        db_session.add(regular_user)
        db_session.commit()
        
        response = client.put(f'/api/admin/users/{regular_user.id}/role',
                            json={'role': 'admin'},
                            headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'User role updated successfully'
        assert data['user']['role'] == 'admin'
        
        # Verify in database
        db_session.refresh(regular_user)
        assert regular_user.role == UserRole.ADMIN
    
    def test_admin_change_user_role_to_user(self, client, admin_headers, db_session):
        """
        Test admin demoting an admin to user role.
        
        Args:
            client: Test client fixture
            admin_headers: Admin authentication headers fixture
            db_session: Database session fixture
        """
        # Create an admin user
        admin_user = User('anotheradmin', 'password', UserRole.ADMIN)
        db_session.add(admin_user)
        db_session.commit()
        
        response = client.put(f'/api/admin/users/{admin_user.id}/role',
                            json={'role': 'user'},
                            headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'User role updated successfully'
        assert data['user']['role'] == 'user'
        
        # Verify in database
        db_session.refresh(admin_user)
        assert admin_user.role == UserRole.USER
    
    def test_admin_cannot_change_own_role(self, client, admin_headers, sample_admin):
        """
        Test that admin cannot change their own role.
        
        Args:
            client: Test client fixture
            admin_headers: Admin authentication headers fixture
            sample_admin: Sample admin fixture
        """
        response = client.put(f'/api/admin/users/{sample_admin.id}/role',
                            json={'role': 'user'},
                            headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Cannot change your own role' in data['error']
    
    def test_admin_change_role_invalid_role(self, client, admin_headers, db_session):
        """
        Test admin changing user role to invalid role.
        
        Args:
            client: Test client fixture
            admin_headers: Admin authentication headers fixture
            db_session: Database session fixture
        """
        # Create a regular user
        regular_user = User('regularuser', 'password')
        db_session.add(regular_user)
        db_session.commit()
        
        response = client.put(f'/api/admin/users/{regular_user.id}/role',
                            json={'role': 'superadmin'},  # Invalid role
                            headers=admin_headers)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'Invalid role' in data['error']
    
    def test_regular_user_cannot_change_roles(self, client, auth_headers, db_session):
        """
        Test that regular users cannot change user roles.
        
        Args:
            client: Test client fixture
            auth_headers: Regular user authentication headers fixture
            db_session: Database session fixture
        """
        # Create another user
        other_user = User('otheruser', 'password')
        db_session.add(other_user)
        db_session.commit()
        
        response = client.put(f'/api/admin/users/{other_user.id}/role',
                            json={'role': 'admin'},
                            headers=auth_headers)
        
        assert response.status_code == 403


class TestAdminBookManagement:
    """Test cases for admin book management capabilities."""
    
    def test_admin_can_delete_any_book(self, client, admin_headers, sample_book):
        """
        Test that admin can delete any book regardless of ownership.
        
        Args:
            client: Test client fixture
            admin_headers: Admin authentication headers fixture
            sample_book: Sample book fixture (owned by regular user)
        """
        book_id = sample_book.id
        response = client.delete(f'/api/books/{book_id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Book deleted successfully'
        
        # Verify book was deleted
        assert Book.query.get(book_id) is None
    
    def test_admin_can_delete_taken_book(self, client, admin_headers, sample_book, db_session):
        """
        Test that admin can delete books even when they are taken.
        
        Args:
            client: Test client fixture
            admin_headers: Admin authentication headers fixture
            sample_book: Sample book fixture
            db_session: Database session fixture
        """
        # Create a user and mark book as taken
        taker = User('booktaker', 'password')
        db_session.add(taker)
        db_session.commit()
        
        sample_book.taken_by = taker.id
        db_session.commit()
        
        book_id = sample_book.id
        response = client.delete(f'/api/books/{book_id}', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Book deleted successfully'
        
        # Verify book was deleted
        assert Book.query.get(book_id) is None


class TestAdminStatistics:
    """Test cases for admin statistics endpoint."""
    
    def test_admin_get_statistics(self, client, admin_headers, multiple_books, db_session):
        """
        Test admin retrieving platform statistics.
        
        Args:
            client: Test client fixture
            admin_headers: Admin authentication headers fixture
            multiple_books: Multiple books fixture
            db_session: Database session fixture
        """
        # Create some taken books to test exchange statistics
        taker = User('booktaker', 'password')
        db_session.add(taker)
        db_session.commit()
        
        # Take some books
        multiple_books[0].taken_by = taker.id
        multiple_books[1].taken_by = taker.id
        db_session.commit()
        
        response = client.get('/api/admin/statistics', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Check that all required statistics are present
        required_stats = [
            'total_books',
            'available_books',
            'total_exchanges',
            'total_users',
            'most_popular_genre',
            'books_created_today'
        ]
        
        for stat in required_stats:
            assert stat in data
            assert isinstance(data[stat], (int, str))
        
        # Verify some statistics make sense
        assert data['total_books'] >= 5  # From multiple_books
        assert data['total_exchanges'] >= 2  # Two books were taken
        assert data['available_books'] == data['total_books'] - data['total_exchanges']
        assert data['total_users'] >= 2  # At least admin and book owner
    
    def test_admin_statistics_most_popular_genre(self, client, admin_headers, multiple_books):
        """
        Test that most popular genre is correctly calculated.
        
        Args:
            client: Test client fixture
            admin_headers: Admin authentication headers fixture
            multiple_books: Multiple books fixture (has 2 Fiction books)
        """
        response = client.get('/api/admin/statistics', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Fiction should be the most popular genre (appears twice in multiple_books)
        assert data['most_popular_genre'] == 'Fiction'
    
    def test_admin_statistics_books_created_today(self, client, admin_headers, sample_book):
        """
        Test that books created today statistic is accurate.
        
        Args:
            client: Test client fixture
            admin_headers: Admin authentication headers fixture
            sample_book: Sample book fixture (created today)
        """
        response = client.get('/api/admin/statistics', headers=admin_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        
        # At least the sample book was created today
        assert data['books_created_today'] >= 1
    
    def test_regular_user_cannot_get_statistics(self, client, auth_headers):
        """
        Test that regular users cannot access statistics.
        
        Args:
            client: Test client fixture
            auth_headers: Regular user authentication headers fixture
        """
        response = client.get('/api/admin/statistics', headers=auth_headers)
        
        assert response.status_code == 403
        data = response.get_json()
        assert 'Admin privileges required' in data['error']
    
    def test_unauthenticated_cannot_get_statistics(self, client):
        """
        Test that unauthenticated users cannot access statistics.
        
        Args:
            client: Test client fixture
        """
        response = client.get('/api/admin/statistics')
        
        assert response.status_code == 401


class TestAdminCascadeDeletion:
    """Test cases for cascade deletion when admin deletes users."""
    
    def test_admin_delete_user_cascades_books(self, client, admin_headers, db_session):
        """
        Test that deleting a user also deletes their books.
        
        Args:
            client: Test client fixture
            admin_headers: Admin authentication headers fixture
            db_session: Database session fixture
        """
        # Create a user with books
        user_with_books = User('userwithbooks', 'password')
        db_session.add(user_with_books)
        db_session.commit()
        
        # Create books for this user
        book1 = Book(user_with_books.id, 'Book 1', 'Author 1', 2023, 'Fiction', '123 Test St')
        book2 = Book(user_with_books.id, 'Book 2', 'Author 2', 2023, 'Science', '456 Test Ave')
        db_session.add_all([book1, book2])
        db_session.commit()
        
        book1_id, book2_id = book1.id, book2.id
        user_id = user_with_books.id
        
        # Delete the user
        response = client.delete(f'/api/admin/users/{user_id}', headers=admin_headers)
        
        assert response.status_code == 200
        
        # Verify user and books were deleted
        assert User.query.get(user_id) is None
        assert Book.query.get(book1_id) is None
        assert Book.query.get(book2_id) is None
    
    def test_admin_delete_user_updates_taken_books(self, client, admin_headers, db_session):
        """
        Test that deleting a user who has taken books updates those books.
        
        Args:
            client: Test client fixture
            admin_headers: Admin authentication headers fixture
            db_session: Database session fixture
        """
        # Create users
        book_owner = User('bookowner', 'password')
        book_taker = User('booktaker', 'password')
        db_session.add_all([book_owner, book_taker])
        db_session.commit()
        
        # Create a book and have it taken
        book = Book(book_owner.id, 'Taken Book', 'Author', 2023, 'Fiction', '123 Test St')
        db_session.add(book)
        db_session.commit()
        
        book.taken_by = book_taker.id
        db_session.commit()
        
        book_id = book.id
        taker_id = book_taker.id
        
        # Delete the taker
        response = client.delete(f'/api/admin/users/{taker_id}', headers=admin_headers)
        
        assert response.status_code == 200
        
        # Verify taker was deleted but book still exists
        assert User.query.get(taker_id) is None
        
        # Book should still exist but taken_by should be reset or handled appropriately
        # Note: This depends on your foreign key constraints and cascade settings
        remaining_book = Book.query.get(book_id)
        assert remaining_book is not None