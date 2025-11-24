from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Session
# NOTE: We remove the 'from sqlalchemy.ext.asyncio import ...' imports
from app.core.config import settings
from typing import Generator
import logging

# setting up logging for easier debugging
logging.basicConfig(level=logging.INFO)

# 1. BASE CLASS FOR DECLARATIVE MODELS

class Base(DeclarativeBase):
    """
    Base class which provides automated table names and 
    a base method for string representation of instances.
    """
    pass

# 2. Synchronous engine and session factory
# IMPORTANT CHANGE: Use create_engine (synchronous)
try:
    # Use a standard synchronous driver URL (e.g., 'postgresql+psycopg2://' instead of 'postgresql+asyncpg://')
    # NOTE: Your settings.Database_URL MUST use a synchronous driver now.
    engine = create_engine(settings.Database_URL, echo=True)

    # sessionmaker creates a configured session class
    # IMPORTANT CHANGE: Use sessionmaker (synchronous)
    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=Session, # Explicitly use the standard synchronous Session
        expire_on_commit=False,
    )
    logging.info("SQLAlchemy synchronous engine and session created successfully.")

except Exception as e:
    logging.error(f"Error creating SQLAlchemy components: {e}")
    # You might want to raise the exception or handle it more gracefully
    raise e


# 3. Dependency Injection for FastAPI
# IMPORTANT CHANGE: This function is now synchronous (no 'async' keyword)
def get_db() -> Generator[Session, None, None]:
    """
    Dependency to get a database session.
    Yields a synchronous Session and automatically closes it afterwards.
    """
    db = SessionLocal()
    try:
        # NOTE: We use 'yield' instead of 'await session.close()'
        yield db
    finally:
        db.close()


---

## 🚦 Required Code Checks for Synchronous Switch

Switching to a synchronous stack requires changes across three main areas of your application:

### 1. Database Connection URL (CRITICAL)

The URL specified in your `settings.Database_URL` **must be updated** to use a synchronous database driver.

| Database | Asynchronous (Old) | **Synchronous (New)** |
| :--- | :--- | :--- |
| **PostgreSQL** | `postgresql+asyncpg://...` | **`postgresql+psycopg2://...`** |
| **MySQL** | `mysql+aiomysql://...` | **`mysql+pymysql://...`** |
| **SQLite** | `sqlite+aiosqlite://...` | **`sqlite:///./sql_app.db`** |

**Action:** Verify that your `settings.Database_URL` is using the correct synchronous driver for your database.

### 2. CRUD Functions (`app/crud/user.py`)

All the code I generated in the previous step (for asynchronous CRUD) must be reverted to its synchronous form:

* **Remove** all `async` keywords from function definitions (`async def`).
* **Remove** all `await` keywords from database calls (`await db.execute(...)`).
* **Replace** `db.execute(select(...))` with the traditional synchronous `db.query(...).filter(...).all()` or similar methods.

**Action:** Use the original **Synchronous CRUD code** I provided in my second response, as it is already correct for this setup.

### 3. API Endpoints (`app/api/v1/endpoints/router.py`)

The router functions must also be changed to synchronous:

* **Remove** the `async` keyword from `async def` function definitions.
* **Remove** all `await` keywords before calling CRUD functions.
* **Change** the injected dependency type from `AsyncSession` to `Session`.

**Action:** Use the original **Synchronous Router code** I provided in my second response.