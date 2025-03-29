from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from app.models import Setting
from app.db import get_async_session
from app.auth import basic_auth
from app.services.prompt_service import prompt_service  # Import the prompt service

router = APIRouter()
templates = Jinja2Templates(directory = "templates")


# Function to load all prompts from the prompts directory
def load_all_prompts():
    """Load all available prompts from the prompts directory"""
    print("Debug: Loading all prompts from files")
    print(f"Debug: Type of prompts_dir: {type(prompt_service.prompts_dir)}")

    prompts = {}
    # Get list of JSON files in the prompts directory
    prompt_files = [f.stem for f in prompt_service.prompts_dir.glob("*.json") if f.is_file()]

    # Load each prompt
    for prompt_name in prompt_files:
        # Skip API-specific prompts (those with an underscore)
        if "_" in prompt_name:
            continue
        try:
            prompt_data = prompt_service.get_prompt(prompt_name)
            prompts[prompt_name] = prompt_data["base_prompt"]
            print(f"Debug: Loaded prompt: {prompt_name}")
        except Exception as e:
            print(f"Debug: Error loading prompt {prompt_name}: {str(e)}")

    print(f"Debug: Loaded {len(prompts)} prompts: {list(prompts.keys())}")
    return prompts


@router.get("/settings", response_class = HTMLResponse)
async def get_settings(
        request: Request,
        user: dict = Depends(basic_auth),
        session: AsyncSession = Depends(get_async_session)
):
    print(f"Debug: Fetching (from db) settings for user {user.id}")
    try:
        result = await session.execute(
            select(Setting)
            .where(Setting.user_id == user.id)
            .order_by(Setting.updated_at.desc())
        )
        settings = result.scalar_one_or_none()
        print(f"Debug: Settings data type: {type(settings)}")
        if settings is not None:
            print("Debug: Settings content:", settings.__dict__)
        else:
            print("Debug: No settings found for user")

        # Load all available prompts from files
        predefined_prompts = load_all_prompts()

        return templates.TemplateResponse("settings.html", {
            "request": request,
            "settings": settings,
            "predefined_prompts": predefined_prompts
        })
    except Exception as e:
        print(f"Error loading settings: {str(e)}")
        raise HTTPException(status_code = 500, detail = "Settings load failed")


@router.post("/settings", response_class = HTMLResponse)
async def post_settings(
        request: Request,
        ai_model: str = Form(...),
        temperature: str = Form(...),
        max_tokens: int = Form(...),
        response_max_length: str = Form(...),
        base_prompt_type: str = Form(...),
        user: dict = Depends(basic_auth),
        session: AsyncSession = Depends(get_async_session),
        use_base64_image: bool = Form(False)
):
    print(f"Debug: Saving settings for user {user.id}")
    print(f"Debug: Form data - model: {type(ai_model)}, temperature: {type(temperature)}")
    print(f"Debug: Form data - max_tokens: {type(max_tokens)}, response_max_length: {type(response_max_length)}")
    print(f"Debug: Form data - base_prompt_type: {type(base_prompt_type)}")

    try:
        # Load all available prompts
        predefined_prompts = load_all_prompts()

        # Validate inputs
        if ai_model not in ["gpt-4o-mini"]:
            raise ValueError("Invalid ai model selection")
        try:
            temp = float(temperature)
            if temp < 0 or temp > 2:
                raise ValueError("Temperature must be between 0 and 2")
        except ValueError:
            raise ValueError("Temperature must be a valid number")
        if max_tokens < 100 or max_tokens > 2000:
            raise ValueError("Max tokens must be between 100 and 2000")
        if response_max_length not in ["short", "medium", "long"]:
            raise ValueError("Invalid response length")
        if base_prompt_type not in predefined_prompts:
            raise ValueError("Invalid prompt type selection")

        # Get the prompt data from file
        prompt_data = prompt_service.get_prompt(base_prompt_type)
        base_default_prompt = prompt_data["base_prompt"]

        # Check if settings already exist for the user
        result = await session.execute(
            select(Setting).where(Setting.user_id == user.id)
        )
        existing_settings = result.scalar_one_or_none()
        print(f"Debug: existing_settings type: {type(existing_settings)}")

        if existing_settings:
            print("Debug: Updating existing settings")
            existing_settings.ai_model = ai_model
            existing_settings.temperature = temperature
            existing_settings.max_tokens = max_tokens
            existing_settings.response_max_length = response_max_length
            existing_settings.base_prompt_type = base_prompt_type
            existing_settings.base_default_prompt = base_default_prompt
            existing_settings.updated_at = datetime.utcnow()
            existing_settings.use_base64_image = use_base64_image
        else:
            print("Debug: Creating new settings record")
            new_settings = Setting(
                user_id = user.id,
                ai_model = ai_model,
                temperature = temperature,
                max_tokens = max_tokens,
                response_max_length = response_max_length,
                base_prompt_type = base_prompt_type,
                base_default_prompt = base_default_prompt,
                use_base64_image = use_base64_image,
                created_at = datetime.utcnow(),
                updated_at = datetime.utcnow()
            )
            session.add(new_settings)

        await session.commit()
        print("Debug: Settings saved successfully for user", user.id)
        return RedirectResponse(url = "/dashboard", status_code = 303)
    except ValueError as e:
        print(f"Validation error: {str(e)}")
        # Load prompts again for the error response
        predefined_prompts = load_all_prompts()
        return templates.TemplateResponse("settings.html", {
            "request": request,
            "error": str(e),
            "predefined_prompts": predefined_prompts
        })
    except Exception as e:
        print(f"Error saving settings: {str(e)}")
        raise HTTPException(status_code = 500, detail = "Settings save failed")
