# File: app/routes/settings.py
from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from app.models import Setting
from app.db import get_async_session
from app.auth import basic_auth

router = APIRouter()
templates = Jinja2Templates(directory = "templates")


@router.get("/settings", response_class = HTMLResponse)
async def get_settings(
        request: Request,
        user: dict = Depends(basic_auth),
        session: AsyncSession = Depends(get_async_session)
):
    print(f"Debug: Loading settings for user {user.id}")
    try:
        result = await session.execute(
            select(Setting)
            .where(Setting.user_id == user.id)
            .order_by(Setting.updated_at.desc())
        )
        settings = result.scalar_one_or_none()
        print(f"Debug: Settings data type: {type(settings)}")

        return templates.TemplateResponse("settings.html", {
            "request": request,
            "settings": settings
        })
    except Exception as e:
        print(f"Error loading settings: {str(e)}")
        raise HTTPException(status_code = 500, detail = "Settings load failed")


@router.post("/settings", response_class = HTMLResponse)
async def post_settings(
        request: Request,
        photo_resolution: str = Form(...),
        file_size_limit: str = Form(...),
        openai_prompt_base: str = Form(...),
        tone: str = Form(...),
        length: str = Form(...),
        user: dict = Depends(basic_auth),
        session: AsyncSession = Depends(get_async_session)
):
    print(f"Debug: Saving settings for user {user.id}")
    try:
        # Validate inputs
        if photo_resolution not in ["720p", "1080p"]:
            raise ValueError("Invalid photo resolution")
        if file_size_limit not in ["64kB", "128kB"]:
            raise ValueError("Invalid file size limit")
        if not openai_prompt_base.strip():
            raise ValueError("Prompt base cannot be empty")

        # Create new settings entry
        new_settings = Setting(
            user_id = user.id,
            photo_resolution = photo_resolution,
            file_size_limit = file_size_limit,
            openai_prompt_base = openai_prompt_base,
            tone = tone,
            length = length,
            created_at = datetime.utcnow(),
            updated_at = datetime.utcnow()
        )

        session.add(new_settings)
        await session.commit()
        print(f"Debug: Settings saved with ID {new_settings.id}")

        return RedirectResponse(url = "/dashboard", status_code = 303)
    except ValueError as e:
        print(f"Validation error: {str(e)}")
        return templates.TemplateResponse("settings.html", {
            "request": request,
            "error": str(e)
        })
    except Exception as e:
        print(f"Error saving settings: {str(e)}")
        raise HTTPException(status_code = 500, detail = "Settings save failed")
