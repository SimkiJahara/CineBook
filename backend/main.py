from fastapi import FastAPI
from app.routes.city_routes import router as city_router
from app.database import init_db
from app.routes.address_routes import router as address_router
from app.routes.theater_routes import router as theater_router



app = FastAPI(
    title="CineBook Backend",
    description="Testing environment for Tanmoy's branch",
    version="1.0",
)

# Create tables in the database on startup
init_db()

# include your city routes
app.include_router(city_router)
app.include_router(address_router)
app.include_router(theater_router)


@app.get("/")
def root():
    return {"message": "Backend is running!"}
