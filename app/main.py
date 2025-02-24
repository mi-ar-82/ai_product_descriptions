# app/main.py
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from app.routes import router, html_auth
from app.db import engine
from app.models import Base
from app.config import settings

# Lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Debug: Starting FastAPI application lifespan")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

# Create FastAPI app
app = FastAPI(lifespan=lifespan)

# Add session middleware for authentication
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    same_site="Lax",
    https_only=False  # Allow HTTP
)
print("Debug: Session middleware added to FastAPI app")


# Include routes
app.include_router(router)
app.include_router(html_auth.router)
print("Debug: Routers included in FastAPI app")

# Configure templates
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.get("/")
async def root():
    print("Debug: Root endpoint accessed")
    return {"message": "Welcome to the AI Product Descriptions App"}
