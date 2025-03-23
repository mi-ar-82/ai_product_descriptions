# File: app/routes/dashboard.py
from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.future import select
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
import traceback
import os
from app.models import UploadedFile, Setting
from app.db import get_async_session
from app.auth import basic_auth
from app.models import Product, UploadedFile, User



router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    user: User = Depends(basic_auth),
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
            "user": user,  # Pass the user directly
            "files": files,
            "settings": current_settings
        })
    except Exception as e:
        print(f"Error loading dashboard: {str(e)}")
        traceback.print_exc()  # This line is crucial for debugging
        raise HTTPException(status_code = 500, detail = f"Dashboard load failed: {str(e)}")




@router.post("/clear-data")
async def clear_all_data(
        request: Request,
        user: User = Depends(basic_auth),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        print(f"Debug: User object type before operations: {type(user)}")
        print(f"Debug: User object before operations: {user}")

        # Ensure user remains a User object
        if not isinstance(user, User):
            raise TypeError("Expected user to be an instance of User")

        # Proceed with data clearing logic - using ORM delete
        await session.execute(delete(Product).where(Product.user_id == user.id))

        # Using proper ORM query to get UploadedFile objects
        uploaded_files_result = await session.execute(
            select(UploadedFile).where(UploadedFile.user_id == user.id)
        )
        uploaded_files = uploaded_files_result.scalars().all()

        for file in uploaded_files:
            file_path = os.path.join("temp", f"{file.id}_{file.file_name}")
            if os.path.exists(file_path):
                os.remove(file_path)

        # Using ORM delete for consistency
        await session.execute(delete(UploadedFile).where(UploadedFile.user_id == user.id))
        await session.commit()

        print(f"Debug: Data cleared successfully for user {user.id}")
        return RedirectResponse(url = "/dashboard?message=All data has been cleared successfully.", status_code = 303)
    except Exception as e:
        print(f"Error clearing data: {str(e)}")
        await session.rollback()
        return RedirectResponse(url = f"/dashboard?error=An error occurred while clearing data: {str(e)}",
                               status_code = 303)
