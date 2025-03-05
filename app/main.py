# File: app/main.py
import os
import logging
import builtins
from app.logger import logging_configurator
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler
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

# Environment-controlled logging (set via .env or OS environment)
LOG_ENABLED = False  # Set to False to disable
LOG_LEVEL = logging.DEBUG  # Set to desired level

logging_configurator.configure_logging(
    enable=LOG_ENABLED,
    log_level=LOG_LEVEL
)


@app.middleware("http")
async def session_middleware(request: Request, call_next):
    session_cookie = request.cookies.get("session")
    if session_cookie:
        try:
            user = await get_user_manager().get_session(session_cookie)
            request.state.user = user
        except Exception as e:
            print(f"Session validation error: {str(e)}")

    logger.debug(f"-> Request {request.method} {request.url}")
    response = await call_next(request)
    logger.debug(f"<- Response {response.status_code} {request.url}")
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
