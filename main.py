"""
The main application file for the Ticketing API.

This module initializes the FastAPI application, configures middleware (CORS),
sets up the application lifespan (startup/shutdown events), initializes the
database, includes all API routers, and starts the background scheduler for
managing seat holds.
"""

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

from app.core.config import settings
from app.core.db import Base, engine

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
from app.models.movie import Movie
from app.models.screen import Screen
from app.models.show import Screening
from app.models.seat import ShowSeat, Seat, Booking, BookedSeat
from app.services.scheduler import release_expired_holds_job_sync # Needs to be imported for start_scheduler


# --- SCHEDULER CONFIGURATION ---
scheduler = BackgroundScheduler()

def start_scheduler():
    """
    Configures and starts the background scheduler for cleaning up expired holds.

    The job is set to run every 30 seconds to release seats that have been
    held for too long (expired hold duration is typically 180 seconds).
    """
    
    # Add the cleanup job: runs every 30 seconds
    # The interval MUST be much shorter than the seat hold duration (180s)
    scheduler.add_job(
        release_expired_holds_job_sync,
        'interval',
        seconds=30,
        id='release_expired_holds',
        replace_existing=True
    )
    scheduler.start()
    print("🎬 Background Scheduler started: Seat cleanup running every 30 seconds.")
    #

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles startup and shutdown events using FastAPI's lifespan context manager.

    **Startup:**
    1. Creates all database tables via SQLAlchemy's Base metadata.
    2. Starts the background scheduler for seat hold cleanup.

    **Shutdown:**
    1. Gracefully shuts down the background scheduler.

    :param app: The FastAPI application instance.
    :yields: Control back to the application to handle requests.
    """
    # === Startup Events ===
    print("Application startup...")
    print("Database startup: Attempting to create all tables...")
    # This call relies on all models being imported above ⬆️
    Base.metadata.create_all(bind=engine)
    print("Database startup: Tables created successfully.")
    
    start_scheduler()
    
    yield # Application can now handle requests

    # === Shutdown Events ===
    print("Application shutdown...")
    if scheduler.running:
        scheduler.shutdown()
        print("Background Scheduler shut down gracefully.")


# 1. Create the main FastAPI application instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url="/openapi.json",
    lifespan=lifespan # Attach the lifespan context manager
)

# 2. Add CORS middleware to allow connections from the frontend (e.g., for WebSockets/HTTP)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allows all origins for development
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
)

# 3. Add a startup event handler to automatically create all database tables
# NOTE: The logic has been moved to the `lifespan` function above, but keeping
# the on_event for potential backward compatibility.
@app.on_event("startup")
def on_startup():
    """
    Creates all database tables defined by SQLAlchemy's Base metadata.

    This ensures the database schema is ready before the application accepts traffic.
    """
    print("Database startup: Attempting to create all tables...")
    # This call relies on all models being imported above ⬆️
    Base.metadata.create_all(bind=engine)
    print("Database startup: Tables created successfully.")

# 4. Include the user router under the base prefix `/v1`
app.include_router(
    user_router,
    prefix="/v1",
    tags=["Users"]
)

# 5. Include the authentication router under the base prefix `/v1`
app.include_router(
    auth_router,
    prefix="/v1",
    tags=["Authentication"]
)

# 6. Include the bookings router under the base prefix `/v1`
app.include_router(
    bookings_router,
    prefix="/v1",
    tags=["Bookings"]
)

# 7. Include the shows router (which contains the WebSocket endpoint)
app.include_router(
    shows_router,
    prefix="/v1",
    tags=["Shows"]
)

# 8. Add a simple root path endpoint (`/`)
@app.get("/", summary="Root Path")
def read_root():
    """
    Returns a simple welcome message and project details.

    :returns: A dictionary containing a welcome message, version, and documentation link.
    :rtype: dict
    """
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME} API!",
        "version": settings.VERSION,
        "documentation": "/docs"
    }


# Optional: Configuration for running the application directly (for local testing)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)