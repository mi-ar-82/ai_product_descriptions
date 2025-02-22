from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
from io import StringIO
from app.auth import auth_backend
from app.models.user import User
from app.db import get_async_session
from app.users import fastapi_users, UserCreate, UserRead
from app.routes.upload_csv import router as upload_csv_router

router = APIRouter()

# Include FastAPI Users routes for authentication and registration with schemas
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"]
)

# Include the upload CSV route
router.include_router(
    upload_csv_router,
    prefix="/api",
    tags=["CSV Upload"])

current_user = fastapi_users.current_user()
