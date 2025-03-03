# File: app/routes/html_auth.py
import os
import traceback
import logging
from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi_users.manager import BaseUserManager
from app.users import get_user_manager, UserCreate  # Import your user manager and schemas
from app.auth import basic_auth
from app.models.user import User


logger = logging.getLogger(__name__)


router = APIRouter()

current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
templates = Jinja2Templates(directory=os.path.join(project_root, "templates"))



@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    print("Debug: Rendering login page")
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    print("Debug: Rendering register page")
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_class = HTMLResponse)
async def register(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        user_manager = Depends(get_user_manager)
):
    print(f"Debug: Registration attempt started for {email}", flush = True)
    try:
        user_create = UserCreate(email = email, password = password)
        print(f"Debug: UserCreate object: {user_create.model_dump()}", flush = True)

        user = await user_manager.create(user_create)
        print(f"Debug: User created - ID: {user.id}", flush = True)

        return RedirectResponse(url = "/login", status_code = status.HTTP_303_SEE_OTHER)
    except Exception as e:
        print(f"Error: Registration failed - {str(e)}", flush = True)
        print(f"Traceback: {traceback.format_exc()}", flush = True)
        return templates.TemplateResponse("register.html", {
            "request": request,
            "error": str(e)
        })


@router.post("/login", response_class = HTMLResponse)
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    usermanager: BaseUserManager = Depends(get_user_manager),
):
    print("Debug: Attempting to log in user with email:", email)
    print("Debug: Email type:", type(email))  # Debug print for data type
    print("Debug: Password type:", type(password))  # Debug print for data type
    try:
        user = await usermanager.authenticate(email, password)
        print("Debug: Authenticated user:", user)
        if not user:
            return templates.TemplateResponse(
                "login.html", {"request": request, "error": "Invalid credentials"}
            )
        # Redirect to the dashboard after a successful login
        redirect_url = "/dashboard"
        print("Debug: Redirecting to:", redirect_url, "with type:", type(redirect_url))
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_303_SEE_OTHER)
    except Exception as e:
        print("Debug: Login failed:", e)
        return templates.TemplateResponse(
            "login.html", {"request": request, "error": "Login error"}
        )


@router.get("/auth/me")
async def get_current_user(user: User = Depends(basic_auth)):
    print(f"Debug: Fetching current user details for user ID: {user.id}")
    return {"id": user.id, "email": user.email}


@router.get("/logout")
async def logout(request: Request):
    print("Debug: Logout initiated")
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("session")
    return response
