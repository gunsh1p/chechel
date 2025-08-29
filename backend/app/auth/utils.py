"""
Authentication and authorization utility functions for the BookCrossing application.

This module provides utility functions for checking permissions and access rights.
"""


def check_book_ownership_or_admin(current_user, book):
    """
    Check if the current user owns the book or is an admin.
    
    Args:
        current_user: The authenticated user
        book: The book to check ownership for
        
    Returns:
        bool: True if user owns the book or is admin, False otherwise
    """
    return current_user.is_admin() or book.owner_id == current_user.id


def check_book_modification_rights(current_user, book):
    """
    Check if the current user can modify the book.
    
    Args:
        current_user: The authenticated user
        book: The book to check modification rights for
        
    Returns:
        bool: True if user can modify the book, False otherwise
    """
    return book.can_be_modified_by(current_user.id)


def check_book_deletion_rights(current_user, book):
    """
    Check if the current user can delete the book.
    
    Args:
        current_user: The authenticated user
        book: The book to check deletion rights for
        
    Returns:
        bool: True if user can delete the book, False otherwise
    """
    return book.can_be_deleted_by(current_user.id, current_user.is_admin())