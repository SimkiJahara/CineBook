# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # ⬅ NEW

from app.database import init_db
from app.routes.city_routes import router as city_router
from app.routes.address_routes import router as address_router
from app.routes.theater_routes import router as theater_router
from app.routes.hall_routes import router as hall_router
from app.routes.screening_routes import router as screening_router
from app.routes.booking_routes import router as booking_router  # ⬅ add this


app = FastAPI(title="CineBook Backend")

# ✅ CORS settings so React (localhost:3000) can call FastAPI (127.0.0.1:8000)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,          # which frontends can call the API
    allow_credentials=True,
    allow_methods=["*"],            # allow GET, POST, etc.
    allow_headers=["*"],            # allow all headers
)

# include routers
app.include_router(city_router)
app.include_router(address_router)
app.include_router(theater_router)
app.include_router(hall_router)
app.include_router(screening_router)
app.include_router(booking_router)  # ⬅ and include it

@app.get("/")
def root():
    return {"message": "CineBook backend is running"}


# create tables when server starts
init_db()
