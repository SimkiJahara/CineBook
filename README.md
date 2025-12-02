# =============================================================================
# FastAPI Authentication Demo - README
# =============================================================================

# FastAPI Authentication Demo

A production-ready FastAPI authentication system with JWT tokens and PostgreSQL.

## 📁 Project Structure

```
fastapi-auth/
├── .env                    # Environment variables (NEVER commit to git)
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies
├── run.py                  # Application entry point
├── setup_db.py             # Database initialization script
└── app/
    ├── __init__.py
    ├── main.py             # FastAPI application factory
    ├── core/               # Core configuration and security
    │   ├── __init__.py
    │   ├── config.py       # Pydantic settings (loads from .env)
    │   ├── security.py     # Password hashing & JWT functions
    │   └── dependencies.py # FastAPI authentication dependencies
    ├── db/                 # Database configuration
    │   ├── __init__.py
    │   └── session.py      # SQLAlchemy engine and session
    ├── models/             # SQLAlchemy ORM models
    │   ├── __init__.py
    │   ├── user.py         # User model
    │   └── role.py         # Role model
    ├── schemas/            # Pydantic schemas (request/response)
    │   ├── __init__.py
    │   ├── user.py         # User schemas
    │   ├── token.py        # Token schemas
    │   └── role.py         # Role schemas
    ├── services/           # Business logic / CRUD operations
    │   ├── __init__.py
    │   ├── user_service.py # User CRUD operations
    │   └── role_service.py # Role CRUD operations
    └── routers/            # API route handlers
        ├── __init__.py
        ├── auth.py         # Authentication endpoints
        └── users.py        # User management endpoints
```

## 🔐 Security Improvements Over Tutorial

| Original Article | This Implementation |
|-----------------|---------------------|
| `SECRET_KEY = "your-secret-key-here"` (hardcoded) | Loaded from `.env` file |
| `DATABASE_URL = "sqlite:///./auth.db"` (hardcoded) | Loaded from `.env` file |
| Flat file structure | Modular `app/` directory |
| Pydantic V1 `Config` class | Pydantic V2 `model_config` |
| SQLite database | PostgreSQL (production-ready) |

## 🚀 Setup Instructions

### 1. Create Virtual Environment

```bash
cd fastapi-auth
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

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

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message |
| GET | `/health` | Health check |
| POST | `/api/v1/auth/token` | Login (get JWT token) |
| POST | `/api/v1/users/register` | Register new user |
| GET | `/api/v1/users/me` | Get current user profile |
| GET | `/api/v1/users/` | List all users |

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

## 📝 License

MIT License
