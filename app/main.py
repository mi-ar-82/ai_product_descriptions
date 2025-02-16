from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.routes import router
from app.db import engine
from app.models import Base

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

# Optional: Add a root endpoint for testing
@app.get("/")
async def root():
    return {"message": "Welcome to the AI Product Descriptions App"}
