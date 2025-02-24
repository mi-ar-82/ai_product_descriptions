# File: app/routes/html_auth.py
import os
from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi_users.manager import BaseUserManager
from app.users import get_user_manager, UserCreate  # Import your user manager and schemas

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

@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    user_manager=Depends(get_user_manager)
):
    print(f"Debug: Attempting to register user with email: {email}")
    try:
        # Convert form data to the expected schema for registration
        user_create = UserCreate(email=email, password=password)
        # Create the user using your user manager
        await user_manager.create(user_create)
        # Redirect to login page after successful registration
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        # In case of error, re-render the registration page with an error message
        return templates.TemplateResponse("register.html", {"request": request, "error": str(e)})


@router.post("/login", response_class = HTMLResponse)
async def login(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        user_manager: BaseUserManager = Depends(get_user_manager),
):
    print(f"Debug: Attempting to log in user with email: {email}")
    try:
        user = await user_manager.authenticate({"email": email, "password": password})
        if not user:
            return templates.TemplateResponse("login.html",
                                              {"request": request, "error": "Invalid credentials"})

        # Cookie will be set automatically by auth_backend
        return RedirectResponse(url = "/", status_code = 302)

    except Exception as e:
        return templates.TemplateResponse("login.html",
                                          {"request": request, "error": "Login failed"})
