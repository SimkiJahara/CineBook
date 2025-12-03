# =============================================================================
# FastAPI Application Main Module
# =============================================================================
# Main application factory and configuration.
# This is the core entry point for the FastAPI application.
# =============================================================================
"""
Main application factory and configuration for the FastAPI demo.

This module is the core entry point for the FastAPI application, handling
initialization, middleware configuration, router inclusion, and
application-level lifecycle events.
"""
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.core.config import get_settings
from app.db.session import engine, Base
from app.routers import auth_router, users_router, bookings_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan handler.

    Creates database tables on startup (if they don't exist).
    This replaces the deprecated startup/shutdown events in FastAPI.

    :param app: The FastAPI application instance.
    :type app: fastapi.FastAPI
    :yield: None. The application yields control back to FastAPI after startup.
    :rtype: typing.AsyncGenerator
    """
    # Startup: Create tables
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown: cleanup if needed
    pass


def create_application() -> FastAPI:
    """
    Application factory function.

    Creates and configures the FastAPI application instance.
    This pattern allows for easy testing and multiple configurations.

    Configurations include:
    - Loading settings from environment variables.
    - Setting up CORS middleware.
    - Including API routers (auth, users, bookings).
    - Mounting static directories for frontend resources.

    :return: Configured FastAPI application instance.
    :rtype: fastapi.FastAPI
    """
    settings = get_settings() #loads env from config.py

    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="""
        ## FastAPI Authentication Demo
        
        A production-ready authentication system with:
        - JWT token-based authentication
        - User registration and login
        - Password hashing with bcrypt
        - PostgreSQL database integration
        - Role-based access control
        
        ### Security Improvements over Tutorial
        - Secret keys loaded from environment variables
        - Database URL configured via .env file
        - Modular project structure
        - Proper dependency injection
        """,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # Configure CORS for frontend integration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers with API versioning
    app.include_router(auth_router, prefix="/api/v1")
    app.include_router(users_router, prefix="/api/v1")
    app.include_router(bookings_router, prefix="/api/v1")

    # Mount static files for frontend
    import os

    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
    if os.path.exists(frontend_path):
        app.mount("/static", StaticFiles(directory=frontend_path), name="static")

    # Mount static files for booking app
    app_static_path = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(app_static_path):
        app.mount(
            "/app-static", StaticFiles(directory=app_static_path), name="app-static"
        )

    return app


# Create application instance
app = create_application()


@app.get("/", tags=["Root"])
async def root() -> FileResponse:
    """
    Root endpoint - Serves the frontend login page.

    If the frontend/index.html file exists, it serves that file.
    Otherwise, it returns a default welcome message.

    :return: A FileResponse serving the HTML file or a JSON message.
    :rtype: fastapi.responses.FileResponse or dict
    """
    import os

    frontend_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "frontend", "index.html"
    )
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"message": "Welcome to FastAPI Authentication Demo"}


@app.get("/dashboard", tags=["Root"])
async def dashboard() -> FileResponse:
    """
    Dashboard page - Serves the frontend dashboard.

    If the frontend/dashboard.html file exists, it serves that file.

    :return: A FileResponse serving the HTML file or a JSON message.
    :rtype: fastapi.responses.FileResponse or dict
    """
    import os

    frontend_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "frontend", "dashboard.html"
    )
    if os.path.exists(frontend_path):
        return FileResponse(frontend_path)
    return {"message": "Dashboard not found"}


@app.get("/booking", tags=["Root"])
async def booking_page() -> FileResponse:
    """
    Booking page - Serves the movie ticket booking interface.

    If the app/static/booking.html file exists, it serves that file.

    :return: A FileResponse serving the HTML file or a JSON message.
    :rtype: fastapi.responses.FileResponse or dict
    """
    import os

    booking_path = os.path.join(os.path.dirname(__file__), "static", "booking.html")
    if os.path.exists(booking_path):
        return FileResponse(booking_path)
    return {"message": "Booking page not found"}


@app.get("/health", tags=["Health"])
async def health_check() -> dict:
    """
    Health check endpoint for monitoring.

    Returns application status for load balancers and monitoring tools,
    including the application name and version.

    :return: A dictionary containing the health status and application metadata.
    :rtype: dict
    """
    settings = get_settings()
    return {
        "status": "healthy",
        "version": settings.app_version,
        "app_name": settings.app_name,
    }