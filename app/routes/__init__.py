# File: app/routes/__init__.py

from fastapi import APIRouter, HTTPException, Depends
from app.auth import basic_auth  # basic HTTP authentication dependency
from app.models.user import User
from app.users import UserCreate, UserRead  # Removed fastapi_users since we use basic auth

router = APIRouter()

@router.get("/auth/me")
async def read_current_user(user: User = Depends(basic_auth)):
    print(f"Debug: Fetching current user details for user ID: {user.id}")
    return {"id": user.id, "email": user.email}

# Additional routes (like CSV upload) can be included here
from app.routes.upload_csv import router as upload_csv_router

router.include_router(
    upload_csv_router,
    prefix="/api",
    tags=["CSV Upload"]
)
