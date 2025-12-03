# =============================================================================

# CineBook-Branch Nafisa - README

# =============================================================================

# FastAPI Authentication Demo

Login System & Seat Selection Interface

````text
CineBook-Nafisa/
├── .env                    # Environment variables (NEVER commit to git)
├── .gitignore              # Git ignore rules
├── alembic.ini             # Alembic migration configuration
├── pytest.ini              # Pytest configuration
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
├── setup_db.py             # Database initialization script (Tables, Roles, Seats)
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI application factory
│   ├── core/               # Core configuration and security
│   │   ├── config.py       # Pydantic settings
│   │   ├── security.py     # Password hashing & JWT logic
│   │   └── dependencies.py # Auth & Role dependencies
│   ├── db/                 # Database configuration
│   │   └── session.py      # SQLAlchemy session management
│   ├── models/             # SQLAlchemy ORM models
│   │   ├── user.py         # User model
│   │   ├── role.py         # Role model
│   │   └── booking.py      # Seat & Booking models
│   ├── routers/            # API route handlers
│   │   ├── auth.py         # Login/Token endpoints
│   │   ├── users.py        # User management endpoints
│   │   ├── bookings.py     # Booking system endpoints
│   │   └── owner.py        # Theatre Owner specific endpoints
│   ├── schemas/            # Pydantic schemas
│   │   ├── user.py         # User schemas
│   │   ├── role.py         # Role schemas
│   │   ├── token.py        # Token schemas
│   │   └── booking.py      # Booking & Seat schemas
│   ├── services/           # Business logic layer
│   │   ├── user_service.py
│   │   ├── role_service.py
│   │   └── booking_service.py # Booking logic with race-condition handling
│   └── static/             # Booking App Frontend (Booking UI)
│       ├── booking.html
│       ├── booking.css
│       └── booking.js
├── frontend/               # Auth & Dashboard Frontend
│   ├── index.html          # Login/Register Page
│   ├── dashboard.html      # User Dashboard
│   ├── styles.css
│   └── app.js
├── migrations/             # Database migrations (Alembic)
├── tests/                  # Test suite
│   ├── conftest.py         # Test fixtures
│   ├── test_login.py
│   ├── test_register.py
│   ├── test_booking.py
│   └── test_owner.py
└── docs/                   # Sphinx documentation

## 🔐 Security Improvements Over Tutorial

| Original Article                                   | This Implementation           |
| -------------------------------------------------- | ----------------------------- |
| `SECRET_KEY = "your-secret-key-here"` (hardcoded)  | Loaded from `.env` file       |
| `DATABASE_URL = "sqlite:///./auth.db"` (hardcoded) | Loaded from `.env` file       |
| Flat file structure                                | Modular `app/` directory      |
| Pydantic V1 `Config` class                         | Pydantic V2 `model_config`    |
| SQLite database                                    | PostgreSQL (production-ready) |

## 🚀 Setup Instructions

### 1. Create Virtual Environment

```bash
cd fastapi-auth
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
````

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Edit the `.env` file with your settings:

```env
DATABASE_URL=postgresql://user:password@host/database
SECRET_KEY=your-super-secret-key-generate-with-openssl-rand-hex-32
```

Generate a secure secret key:

```bash
openssl rand -hex 32
```

### 4. Initialize Database

```bash
python setup_db.py
```

### 5. Run the Server

```bash
python run.py
```

Or with uvicorn directly:

```bash
uvicorn app.main:app --reload
```

## 📚 API Endpoints

| Method | Endpoint                 | Description              |
| ------ | ------------------------ | ------------------------ |
| GET    | `/`                      | Welcome message          |
| GET    | `/health`                | Health check             |
| POST   | `/api/v1/auth/token`     | Login (get JWT token)    |
| POST   | `/api/v1/users/register` | Register new user        |
| GET    | `/api/v1/users/me`       | Get current user profile |
| GET    | `/api/v1/users/`         | List all users           |

## 🔑 Authentication Flow

1. **Register**: POST to `/api/v1/users/register` with username, email, password
2. **Login**: POST to `/api/v1/auth/token` with username/password (form data)
3. **Access Protected Routes**: Include JWT in Authorization header:
   ```
   Authorization: Bearer <your_token>
   ```

## 📖 API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 🧪 Example Usage

### Register a User

```bash
curl -X POST "http://localhost:8000/api/v1/users/register" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "full_name": "Test User",
    "password": "securepassword123"
  }'
```

### Login and Get Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=securepassword123"
```

### Access Protected Route

```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <your_token>"
```
