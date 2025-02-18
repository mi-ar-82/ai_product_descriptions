# File: app/routes/html_auth.py
import os
from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.users import get_user_manager, UserCreate  # Import your user manager and schemas

router = APIRouter()

current_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(current_dir, "..", ".."))
templates = Jinja2Templates(directory=os.path.join(project_root, "templates"))



@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register", response_class=HTMLResponse)
async def register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    user_manager=Depends(get_user_manager)
):
    try:
        # Convert form data to the expected schema for registration
        user_create = UserCreate(email=email, password=password)
        # Create the user using your user manager
        await user_manager.create_user(user_create)
        # Redirect to login page after successful registration
        return RedirectResponse(url="/login", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        # In case of error, re-render the registration page with an error message
        return templates.TemplateResponse("register.html", {"request": request, "error": str(e)})

@router.post("/login", response_class=HTMLResponse)
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    # Note: This example assumes you want to implement custom login logic.
    # You might integrate with FastAPI Users' authentication flow here.
    # For simplicity, this stub redirects to the home page upon "login".
    # Properly implement token/session generation and verification as needed.
    # If authentication fails, re-render the login page with an error.
    try:
        # TODO: Implement user authentication using the provided email and password
        # For instance, verify the user's credentials and create a session/token.
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        return templates.TemplateResponse("login.html", {"request": request, "error": str(e)})
