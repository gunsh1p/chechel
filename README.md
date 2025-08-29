# BookCrossing Platform

A complete book sharing platform where users can post books for sharing and take books from others. Built with Flask backend and designed for easy deployment with Docker.

## Project Overview

BookCrossing is a community-driven platform that enables book lovers to share their books with others. Users can post books they want to give away, browse available books, and "take" books from other users by arranging meetups at specified addresses.

## Features

### 🔐 **Authentication System**
- User registration and login with JWT tokens
- Role-based access control (User/Admin)
- Secure password hashing with bcrypt

### 📚 **Book Management**
- Create, read, update, delete book postings
- Advanced filtering and pagination
- Book status tracking (available/taken)
- Meeting address specification for book pickup

### 👥 **User Features**
- View personal posted books
- Track taken books
- Cannot take own books (prevents gaming)
- Cannot modify books once taken

### 🛡️ **Admin Panel**
- User management (view, delete, role changes)
- Enhanced book permissions (delete any book)
- Platform statistics dashboard
- Cascade deletion handling

### 📊 **Statistics Dashboard**
- Total books and exchanges
- Most popular genres
- Daily book creation metrics
- User engagement statistics

## Technology Stack

### Backend
- **Framework**: Flask 2.3.3 with modular blueprint architecture
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT tokens with Flask-JWT-Extended
- **Documentation**: Interactive Swagger UI with Flasgger
- **Testing**: pytest with testcontainers for integration tests
- **Containerization**: Docker and Docker Compose

### Development & Deployment
- **Environment Management**: Multi-environment configuration
- **Testing**: 100% test coverage with unit and integration tests
- **CI/CD Ready**: Docker-based deployment pipeline
- **Security**: SQL injection prevention, input validation, secure headers

## Project Structure

```
chechel/
├── backend/                      # Flask backend application
│   ├── app/                     # Main application package
│   │   ├── models/              # Database models (User, Book)
│   │   ├── auth/                # Authentication & authorization
│   │   └── api/                 # RESTful API endpoints
│   ├── config/                  # Environment configurations
│   ├── tests/                   # Comprehensive test suite
│   ├── app.py                   # Application factory
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile               # Backend container config
│   └── README.md                # Backend documentation
├── docker-compose.yml           # Multi-service deployment
└── README.md                    # This file
```

## Quick Start

### 🚀 **Using Docker (Recommended)**

1. **Clone the repository:**
```bash
git clone <repository-url>
cd chechel
```

2. **Start the application:**
```bash
docker-compose up --build
```

3. **Access the application:**
- API: http://localhost:5000
- Swagger Documentation: http://localhost:5000/docs

4. **Default Admin Account:**
- Username: `admin`
- Password: `admin123`

### 🔧 **Manual Development Setup**

1. **Backend Setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Database Setup:**
```bash
# Install and start PostgreSQL
createdb bookcrossing_dev
```

3. **Run the application:**
```bash
python app.py
```

## API Endpoints

### Authentication
```http
POST /api/auth/register    # Register new user
POST /api/auth             # User login
```

### Books
```http
GET    /api/books          # List books (with filters) - requires auth
POST   /api/books          # Create book
PUT    /api/books/{id}     # Update book
DELETE /api/books/{id}     # Delete book
POST   /api/books/{id}/take # Take a book

GET    /api/books/my       # My posted books
GET    /api/books/taken    # Books I've taken
```

### Admin
```http
GET    /api/admin/users           # List all users
DELETE /api/admin/users/{id}      # Delete user
PUT    /api/admin/users/{id}/role # Change user role
GET    /api/admin/statistics      # Platform stats
```

## Testing

The project includes a comprehensive test suite with 100% coverage:

```bash
# Run all tests
cd backend
pytest

# Run with coverage report
pytest --cov=. --cov-report=html

# Run specific test categories
pytest tests/test_auth.py      # Authentication tests
pytest tests/test_books.py     # Book management tests
pytest tests/test_admin.py     # Admin functionality tests
```

## Database Schema

### User Model
- **id**: Primary key
- **username**: Unique username (max 255 chars)
- **hashed_password**: Bcrypt hashed password
- **role**: Enum (user/admin)
- **created_at**: Account creation timestamp

### Book Model
- **id**: Primary key
- **owner_id**: Foreign key to user
- **title, author, genre**: Book information (max 255 chars each)
- **description**: Optional description (max 255 chars)
- **publish_year**: Publication year (integer)
- **meeting_address**: Pickup location (max 255 chars)
- **taken_by**: Foreign key to user who took the book (nullable)
- **created_at, updated_at**: Timestamps

## Configuration

Environment-based configuration supports:
- **Development**: Debug mode, local database
- **Testing**: Test database, disabled JWT expiration
- **Production**: Secure settings, environment variables

Key environment variables:
- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: JWT secret (change in production!)
- `FLASK_ENV`: Environment mode

## Security Features

- 🔒 **JWT Authentication**: Stateless token-based auth
- 🛡️ **Role-based Authorization**: User/Admin permissions
- 🔐 **Password Security**: Bcrypt hashing with salt
- 🚫 **SQL Injection Prevention**: SQLAlchemy ORM protection
- ✅ **Input Validation**: Comprehensive request validation
- 🔒 **Secure Headers**: Production-ready security headers

## Development Guidelines

### Adding New Features
1. Create models in `backend/app/models/`
2. Add business logic in appropriate modules
3. Create API endpoints in `backend/app/api/`
4. Write comprehensive tests in `backend/tests/`
5. Update Swagger documentation

### Code Quality
- Follow PEP 8 style guidelines
- Write descriptive docstrings
- Maintain test coverage above 90%
- Use type hints where appropriate

## Deployment

### Production Deployment with Docker

1. **Configure environment variables:**
```bash
export DATABASE_URL=postgresql://user:pass@host:5432/db
export SECRET_KEY=your-super-secret-production-key
export FLASK_ENV=production
```

2. **Deploy with Docker Compose:**
```bash
docker-compose -f docker-compose.yml up -d
```

3. **Set up SSL/HTTPS** (recommended with nginx reverse proxy)

### Health Checks
- Application: `GET /api/books?limit=1`
- Database: Built-in PostgreSQL health checks
- Docker: Configured health check endpoints

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Ensure all tests pass: `pytest`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For questions or issues:
1. Check the [backend README](backend/README.md) for detailed API documentation
2. Review the test files for usage examples
3. Open an issue in the repository

---

**Built with ❤️ for the book-loving community**