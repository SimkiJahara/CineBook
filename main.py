from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates

from routers import screening_router

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Include screening routes
app.include_router(screening_router.router)
