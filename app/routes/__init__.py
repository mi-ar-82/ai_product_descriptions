# File: app/routes/__init__.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from app.models.user import User
from app.users import UserCreate, UserRead
from app.routes.html_auth import router as auth_router
from app.routes.upload_csv import router as upload_csv_router


router = APIRouter()

# Include all authentication endpoints (login, register, auth/me, logout)
router.include_router(auth_router, tags=["Authentication"])


# Include CSV upload endpoints under /api
router.include_router(
    upload_csv_router,
    tags=["CSV Upload"]
)
