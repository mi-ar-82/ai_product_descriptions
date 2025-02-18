import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routes import router
from app.routes import html_auth
from app.db import engine
from app.models import Base

from fastapi.templating import Jinja2Templates

# Define a lifespan function for startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic: Initialize the database schema
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # Create all tables at startup
    yield  # Application runs here

# Create the FastAPI app instance with the lifespan function
app = FastAPI(lifespan=lifespan)

# Include the router for API endpoints
app.include_router(router)

app.include_router(html_auth.router)  # Include HTML auth routes

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


# Optional: Add a root endpoint for testing
@app.get("/")
async def root():
    return {"message": "Welcome to the AI Product Descriptions App"}
