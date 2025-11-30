import uvicorn
from fastapi import FastAPI
#from fastapi.staticfiles import StaticFiles
#from fastapi.responses import HTMLResponse
from app.core.config import settings
from app.core.db import Base, engine # Imports Base class for metadata and engine for connection


# Import the APIRouters
from app.api.v1.endpoints.router import router as user_router 
from app.api.v1.endpoints.auth import router as auth_router 
from app.api.v1.endpoints.bookings import router as bookings_router
from app.api.v1.endpoints.shows import router as shows_router

# Import ALL models to ensure they are loaded and registered with SQLAlchemy's Base metadata 
# before table creation in the startup event.
from app.models.users import User
from app.models.theatreowner import TheatreOwner
from app.models.theatre import Theatre
from app.models.buyer import Buyer
from app.models.superadmin import Superadmin 
from app.models.movie import Movie       # <--- CRITICAL: Movie model import
from app.models.screen import Screen     # <--- CRITICAL: Screen model import
from app.models.show import Screening        # <--- CRITICAL: Show model import
from app.models.seat import ShowSeat, Seat, Booking, BookedSeat # All booking models


# 1. Create the main FastAPI application instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url="/openapi.json"
)


# 2. Add a startup event handler to automatically create all database tables
@app.on_event("startup")
def on_startup():
    """
    Creates all database tables defined by SQLAlchemy's Base metadata.
    """
    print("Database startup: Attempting to create all tables...")
    # This call relies on all models being imported above ⬆️
    Base.metadata.create_all(bind=engine)
    print("Database startup: Tables created successfully.")

# 3. Include the user router under the base prefix `/v1`
app.include_router(
    user_router,
    prefix="/v1",
    tags=["Users"] 
)

# 4. Include the authentication router under the base prefix `/v1`
app.include_router(
    auth_router,
    prefix="/v1", 
    tags=["Authentication"] 
)

# 5. Include the bookings router under the base prefix `/v1`
app.include_router(
    bookings_router,
    prefix="/v1", 
    tags=["Bookings"] 
)

# 6. Include the shows router (which contains the WebSocket endpoint)
app.include_router(
    shows_router,
    prefix="/v1", 
    tags=["Shows"] 
)

# 7. Add a simple root path endpoint (`/`)
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