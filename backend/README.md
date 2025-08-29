# BookCrossing API Backend

A Flask-based REST API for a book sharing platform where users can post books for sharing and take books from others.

## Project Structure

```
backend/
├── app/                           # Main application package
│   ├── __init__.py
│   ├── models/                    # Database models
│   │   ├── __init__.py
│   │   ├── base.py               # SQLAlchemy database instance
│   │   ├── user.py               # User model
│   │   └── book.py               # Book model
│   ├── auth/                     # Authentication & authorization
│   │   ├── __init__.py
│   │   ├── decorators.py         # Auth decorators
│   │   └── utils.py              # Auth utility functions
│   └── api/                      # API routes
│       ├── __init__.py
│       ├── auth_routes.py        # Authentication endpoints
│       ├── book_routes.py        # Book management endpoints
│       └── admin_routes.py       # Admin endpoints
├── config/                       # Configuration
│   ├── __init__.py
│   └── config.py                 # Environment configurations
├── tests/                        # Test suite
│   ├── __init__.py
│   ├── conftest.py              # Test fixtures
│   ├── test_auth.py             # Authentication tests
│   ├── test_books.py            # Book management tests
│   └── test_admin.py            # Admin functionality tests
├── app.py                       # Application factory
├── requirements.txt             # Python dependencies
├── pytest.ini                  # Pytest configuration
├── Dockerfile                   # Docker image configuration
├── .dockerignore               # Docker ignore patterns
└── README.md                   # This file
```

## Features

### For Unauthorized Users
- Register a new account
- Log in to existing account

### For Authorized Users (Basic Rights)
- View all books with pagination and filtering
- View their own posted books
- Add new books for sharing
- Update their own books (if not taken yet)
- Delete their own books (if not taken yet)
- Take books from other users
- View books they have taken
- Log out of their account

### For Admin Users
- All regular user functionality
- Delete any book (including taken ones)
- Delete users (along with their books)
- Change user roles (user/admin)
- View user profiles with detailed information
- View platform statistics:
  - Total number of books
  - Most popular genre
  - Number of exchanges
  - Number of new books per day

## Technology Stack

- **Framework**: Flask 2.3.3
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with Flask-JWT-Extended
- **Documentation**: Swagger UI with Flasgger
- **Testing**: pytest, pytest-mock, testcontainers
- **Containerization**: Docker and Docker Compose

## Database Models

### User Model
```
user(
    id: Primary Key,
    username: String(255), Unique,
    hashed_password: String(255),
    role: Enum('user', 'admin'),
    created_at: DateTime
)
```

### Book Model
```
book(
    id: Primary Key,
    owner_id: Foreign Key -> user.id,
    title: String(255),
    description: String(255), Nullable,
    author: String(255),
    publish_year: Integer,
    genre: String(255),
    meeting_address: String(255),
    taken_by: Foreign Key -> user.id, Nullable,
    created_at: DateTime,
    updated_at: DateTime
)
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth` - Login user

### Books
- `GET /api/books` - Get all books with pagination and filters (requires auth)
- `GET /api/books/my` - Get current user's books (requires auth)
- `GET /api/books/taken` - Get books taken by current user (requires auth)
- `POST /api/books` - Create new book (requires auth)
- `PUT /api/books/{id}` - Update book (requires auth + ownership)
- `DELETE /api/books/{id}` - Delete book (requires auth + ownership or admin)
- `POST /api/books/{id}/take` - Take a book (requires auth)

### Admin
- `GET /api/admin/users` - Get all users (admin only)
- `DELETE /api/admin/users/{id}` - Delete user (admin only)
- `PUT /api/admin/users/{id}/role` - Change user role (admin only)
- `GET /api/admin/statistics` - Get platform statistics (admin only)

## Installation and Setup

### Using Docker (Recommended)

1. From the project root directory:
```bash
docker-compose up --build
```

The application will be available at `http://localhost:5000`

### Manual Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL database and update the `DATABASE_URL` in config/config.py

5. Run the application:
```bash
python app.py
```

## Testing

From the backend directory:

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=. --cov-report=html

# Run specific test categories
pytest -m "not slow"  # Skip slow tests
pytest tests/test_auth.py   # Run only auth tests
```

## API Documentation

When the application is running, visit `http://localhost:5000/docs` to access the interactive Swagger documentation.

## Environment Variables

- `SECRET_KEY`: Secret key for JWT tokens (change in production)
- `DATABASE_URL`: PostgreSQL connection string
- `FLASK_ENV`: Environment (development/testing/production)

## Default Admin Account

A default admin account is created when the application starts:
- Username: `admin`
- Password: `admin123`

**Important**: Change the default admin password in production!

## Security Features

- Password hashing with bcrypt
- JWT token authentication
- Role-based authorization
- Input validation and sanitization
- SQL injection protection via SQLAlchemy ORM
- Non-root user in Docker container

## Architecture

The backend follows a modular architecture:

- **`app/models/`**: Database models and relationships
- **`app/auth/`**: Authentication and authorization logic
- **`app/api/`**: RESTful API endpoints organized by blueprint
- **`config/`**: Environment-specific configurations
- **`tests/`**: Comprehensive test suite with fixtures

This structure promotes:
- **Separation of concerns**: Each module has a specific responsibility
- **Testability**: Modular design makes unit testing easier
- **Maintainability**: Clear organization helps with code maintenance
- **Scalability**: Easy to add new features and endpoints