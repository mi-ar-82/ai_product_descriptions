# File: app/main.py

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.db import engine
from app.models import Base

# Import routers from various route modules
from app.routes import router as main_router         # e.g., authentication endpoints (/auth/me)
from app.routes.html_auth import router as html_auth_router  # login and register endpoints
from app.routes.auth import router as auth_router      # logout endpoint
from app.routes.upload_form import router as upload_form_router  # file upload endpoints
from app.routes.settings import router as settings_router  # settings endpoints
from app.routes.download import router as download_router    # file download endpoints

# Lifespan context manager to initialize and shutdown the application
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Debug: Starting FastAPI application lifespan")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("Debug: Database tables created (if not already present)")
    yield
    print("Debug: Application shutdown initiated")

app = FastAPI(lifespan=lifespan)

# Log every incoming request and its response status
@app.middleware("http")
async def log_requests(request: Request, call_next):
    print(f"Debug: Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    print(f"Debug: Response status: {response.status_code} for {request.method} {request.url}")
    return response

# Add session middleware for authentication sessions
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    same_site="Lax",
    https_only=False  # Allow HTTP for development
)
print("Debug: Session middleware added to FastAPI app")

# Determine the project root (one level up from the app folder)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))
print(f"Debug: Project root determined as: {PROJECT_ROOT}")

# Mount the static directory (located at the project root)
static_dir = os.path.join(PROJECT_ROOT, "static")
print(f"Debug: Attempting to mount static files from: {static_dir}")
if not os.path.isdir(static_dir):
    print("ERROR: 'static' directory not found!")
else:
    print(f"Debug: 'static' directory exists at: {static_dir}")
    print(f"Debug: Contents of 'static' directory: {os.listdir(static_dir)}")
app.mount("/static", StaticFiles(directory=static_dir), name="static")
print("Debug: Mounted static files at /static")

# Configure Jinja2 templates directory (located at the project root)
templates_dir = os.path.join(PROJECT_ROOT, "templates")
print(f"Debug: Templates directory set to: {templates_dir}")
templates = Jinja2Templates(directory=templates_dir)

# Include all routers from your routes modules
app.include_router(main_router)
app.include_router(html_auth_router)
app.include_router(auth_router)
app.include_router(upload_form_router)
app.include_router(settings_router)
app.include_router(download_router)
print("Debug: Routers included in FastAPI app")

# Define the root endpoint with a debug print
@app.get("/")
async def root():
    print("Debug: Root endpoint accessed")
    return {"message": "Welcome to the AI Product Descriptions App"}
