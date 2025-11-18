from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine, Base
from app.controllers.movie_controller import router as movie_router

# Create all database tables (runs on startup)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CineBook API",
    description="Movie Booking Platform API",
    version="1.0.0"
)

# CORS middleware — allows frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all movie routes
app.include_router(movie_router)

@app.get("/")
async def root():
    return {"message": "Welcome to CineBook API"}

# Only used when running directly with python main.py
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)