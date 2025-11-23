
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.controllers.movie_controller import router as movie_router


app = FastAPI(
    title="CineBook API",
    description="Movie Booking Platform - Movie Management Module",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware - allows frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:3000",
        "http://localhost:5500",
        "*"  
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include movie routes
app.include_router(movie_router)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint - API info"""
    return {
        "message": "Welcome to CineBook API",
        "status": "online",
        "version": "1.0.0",
        "docs": "/docs",
        "module": "Movie Management & Discovery"
    }


@app.get("/health", tags=["Root"])
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "api": "online"}


# Startup event
@app.on_event("startup")
async def startup():
    print("🎬 CineBook Movie API starting...")
    print("📚 Docs: http://localhost:8000/docs")


# Run with: python -m app.main
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)