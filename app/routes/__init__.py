from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import pandas as pd
from io import StringIO

from app.auth import auth_backend
from app.models.user import User
from app.db import get_async_session
from app.users import fastapi_users, UserCreate, UserRead

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

current_user = fastapi_users.current_user()

@router.post("/upload-csv", tags=["file-upload"])
async def upload_csv(
        file: UploadFile = File(...),
        user: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(400, detail="Invalid file format")

    try:
        contents = await file.read()
        buffer = StringIO(contents.decode('utf-8'))
        df = pd.read_csv(buffer)

        # Validate required columns
        required_columns = {"title", "photo_url"}
        if not required_columns.issubset(df.columns):
            missing = required_columns - set(df.columns)
            raise HTTPException(400, detail=f"Missing required columns: {missing}")

        return {
            "message": "CSV processed successfully",
            "stats": {
                "rows": len(df),
                "columns": list(df.columns)
            }
        }
    except Exception as e:
        raise HTTPException(500, detail=f"Processing error: {str(e)}")
