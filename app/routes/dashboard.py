# File: app/routes/dashboard.py
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import UploadedFile, Setting
from app.db import get_async_session
from app.auth import basic_auth

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user: dict = Depends(basic_auth),
    session: AsyncSession = Depends(get_async_session)
):
    print(f"Debug: Rendering dashboard for user {user.id}")
    try:
        # Get user's uploaded files
        files_result = await session.execute(
            select(UploadedFile)
            .where(UploadedFile.user_id == user.id)
            .order_by(UploadedFile.upload_date.desc())
            .limit(10)
        )
        files = files_result.scalars().all()
        print(f"Debug: Found {len(files)} uploaded files")

        # Get current settings
        settings_result = await session.execute(
            select(Setting)
            .where(Setting.user_id == user.id)
            .order_by(Setting.updated_at.desc())
            .limit(1)
        )
        current_settings = settings_result.scalar_one_or_none()
        print(f"Debug: Current settings type: {type(current_settings)}")

        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "files": files,
            "settings": current_settings
        })
    except Exception as e:
        print(f"Error loading dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail="Dashboard load failed")
