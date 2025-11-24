from sqlalchemy .ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
import logging

#setting up logging for easier debugging (will research more on this)

logging.basicConfig(level=logging.INFO)


#BASE CLASS FOR DECLARATIVE MODELS

class Base(DeclarativeBase):
    """Base class which provides automated table names 
     a base method for string representation of instances."""
    
    pass


# 2. Asynchronous engine and session factory

try:
    engine = create_async_engine(settings.Database_URL, echo=True)


    #async_sessionmaker creates a configured session class 

    AsyncSessionLocal = async_sessionmaker(
        autocommit= False,
        autoflush= False,
        bind= engine,
        class = AsyncSession,
        expire_on_commit=False,
    )
    logging.info("SqlAlchemy engine and session created successfully.")
    except Exception as e:
    logging.error(f"Error creating SQLAlchemy components: {e}")
    # You might want to raise the exception or handle it more gracefully
    # raise e

# 3. Dependency Injection for FastAPI
async def get_db():
    """Dependency to get a database session."""
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()
