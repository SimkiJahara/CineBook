import uvicorn
from fastapi import FastAPI
from app.core.config import settings
from app.core.db import Base, engine # Imports Base class for metadata and engine for connection
from app.api.v1.endpoints.router import router as user_router # Imports the APIRouter for users
from app.models.users import User
from app.models.theatreowner import TheatreOwner
from app.models.theatre import Theatre

from app.models.buyer import Buyer


#you are ensuring that all your model classes are loaded and properly registered with the SQLAlchemy base registry *before* the `startup` event handler tries to use them to create tables. This should finally resolve the `failed to locate a name ('Theatre')` error.

# 1. Create the main FastAPI application instance
# We use the project name and version from settings for documentation purposes
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url="/openapi.json"
)

# 2. Add a startup event handler to automatically create all database tables
# This function is executed asynchronously when the FastAPI application starts up.
@app.on_event("startup")
def on_startup():
    """
    Creates all database tables defined by SQLAlchemy's Base metadata.
    This ensures the database schema is ready before the API handles requests.
    """
    print("Database startup: Attempting to create all tables...")
    # Note: engine is imported from app.core.db, which should be configured 
    # for synchronous operation as per the project requirements.
    Base.metadata.create_all(bind=engine)
    print("Database startup: Tables created successfully.")

# 3. Include the user router under the base prefix `/v1`
# The router itself has a prefix of `/users`, resulting in paths like `/v1/users/create`
app.include_router(
    user_router,
    prefix="/v1",
    tags=["Users"] # Optional: Adds a tag to the OpenAPI docs
)

# 4. Add a simple root path endpoint (`/`)
@app.get("/", summary="Root Path")
def read_root():
    """
    Returns a simple welcome message and project details.
    """
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME} API!",
        "version": settings.VERSION,
        "documentation": "/docs"
    }

# Optional: Configuration for running the application directly (for local testing)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)