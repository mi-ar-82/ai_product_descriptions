# File: app/main.py
import os
import logging
import builtins
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from logging.handlers import RotatingFileHandler

# Override default print behavior globally
_original_print = builtins.print


def flushed_print(*args, **kwargs):
    """Enhanced print that logs to both console and file"""
    kwargs.setdefault('flush', True)
    _original_print(*args, **kwargs)


builtins.print = flushed_print

# Configure logging before other imports
logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers = [
        RotatingFileHandler(
            'app.log',
            maxBytes = 1024 * 1024 * 5,  # 5MB
            backupCount = 3
        ),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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
    print("Debug: Database tables created (if not already present)")
    yield
    print("Debug: Application shutdown initiated")


app = FastAPI(lifespan = lifespan)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.debug(f"→ Incoming {request.method} {request.url}")

    if request.method == "POST":
        try:
            form_data = await request.form()
            logger.debug(f"Form data: {dict(form_data)}")
        except Exception:
            pass

    response = await call_next(request)
    logger.debug(f"← Response {response.status_code} {request.url}")
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

# Static files configuration
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
    print("Debug: Root endpoint accessed, redirecting to login page")
    return RedirectResponse(url = "/login", status_code = 302)
