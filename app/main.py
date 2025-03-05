# File: app/main.py
import os

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.db import engine
from app.models import Base
from app.routes import router as main_router
from app.routes.settings import router as settings_router
from app.routes.download import router as download_router
from app.routes.dashboard import router as dashboard_router




@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Debug: Starting FastAPI application lifespan")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Debug: Database tables created")
    yield
    print("Debug: Application shutdown initiated")


app = FastAPI(lifespan = lifespan)


@app.middleware("http")
async def debug_middleware(request: Request, call_next):
    print(f"Debug: Request to {request.url}")
    response = await call_next(request)
    print(f"Debug: Response {response.status_code}")
    return response


app.add_middleware(
    SessionMiddleware,
    secret_key = settings.SECRET_KEY,
    same_site = "Lax",
    https_only = False
)

# Project root configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

# Static files
static_dir = os.path.join(PROJECT_ROOT, "static")
app.mount("/static", StaticFiles(directory = static_dir), name = "static")

# Templates configuration
templates_dir = os.path.join(PROJECT_ROOT, "templates")
templates = Jinja2Templates(
    directory = templates_dir,
    auto_reload = True,
    autoescape = True,
    trim_blocks = True,
    lstrip_blocks = True
)

# Include routers
app.include_router(main_router)
app.include_router(settings_router)
app.include_router(download_router)
app.include_router(dashboard_router)


@app.get("/")
async def root():
    print("Debug: Redirecting to login from root")
    return RedirectResponse(url = "/login", status_code = 302)


print("Debug: Main application setup complete")
