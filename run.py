#!/usr/bin/env python
# =============================================================================
# Application Entry Point
# =============================================================================
# Root-level entry point for running the FastAPI application.
# Use this file to start the server: python run.py
# =============================================================================

import uvicorn

from app.core.config import get_settings


def main() -> None:
    """
    Main entry point for running the application.

    Starts the Uvicorn ASGI server with the FastAPI application.
    Configuration is loaded from environment variables.
    """
    settings = get_settings()

    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,  # Enable hot reload in debug mode
        log_level="info" if not settings.debug else "debug",
    )


if __name__ == "__main__":
    main()
