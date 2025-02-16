# app/__init__.py
from .main import app  # Import the FastAPI app instance
from .models import Base  # Import SQLAlchemy base class

__all__ = ["app", "Base", "models", "routes", "services"]
