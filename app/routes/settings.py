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

# Define the three pre-written prompts
PREDEFINED_PROMPTS = {
    "conversion": """You are an elite e-commerce copywriter with expertise in conversion optimization. Analyze the provided product image, title, and existing description to create a compelling product description that: (1) highlights key features and benefits, (2) addresses customer pain points, (3) includes sensory language to help customers imagine using the product, (4) incorporates relevant keywords for SEO, and (5) ends with a persuasive call-to-action. Your copy should be scannable with bullet points for key features and maintain a professional yet engaging tone.""",

    "storytelling": """You are a brand storytelling specialist and product copywriter. Your task is to craft an emotionally resonant product description that connects with potential buyers. Examine the provided image, title, and existing description carefully. Create a narrative-driven description that: (1) establishes the product's unique value proposition, (2) weaves in the product's origin story or inspiration if apparent, (3) describes the experience of using the product, (4) highlights premium features visible in the image, and (5) maintains a consistent tone that elevates the perceived value. Balance factual information with aspirational language.""",

    "technical": """You are a technical product specialist and copywriting expert. Your mission is to create a precise, informative, and compelling product description based on the provided image, title, and existing description. Your output should: (1) identify and explain technical specifications visible in the image, (2) translate complex features into clear customer benefits, (3) compare the product to industry standards where relevant, (4) organize information in a logical hierarchy with subheadings and bullet points, and (5) use authoritative language that builds trust. Ensure the description is accessible to both novice and expert customers while maintaining technical accuracy."""
}


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
        return templates.TemplateResponse("settings.html", {
            "request": request,
            "settings": settings,
            "predefined_prompts": PREDEFINED_PROMPTS
        })
    except Exception as e:
        print(f"Error loading settings: {str(e)}")
        raise HTTPException(status_code = 500, detail = "Settings load failed")


@router.post("/settings", response_class = HTMLResponse)
async def post_settings(
        request: Request,
        model: str = Form(...),
        tone: str = Form(...),
        temperature: str = Form(...),
        max_tokens: int = Form(...),
        response_max_length: str = Form(...),
        base_prompt_type: str = Form(...),
        user: dict = Depends(basic_auth),
        session: AsyncSession = Depends(get_async_session),
        use_base64_image: bool = Form(False)
):
    print(f"Debug: Saving settings for user {user.id}")
    print(f"Debug: Form data - model: {type(model)}, tone: {type(tone)}, temperature: {type(temperature)}")
    print(f"Debug: Form data - max_tokens: {type(max_tokens)}, response_max_length: {type(response_max_length)}")
    print(f"Debug: Form data - base_prompt_type: {type(base_prompt_type)}")

    try:
        # Validate inputs (validation code remains unchanged)
        if model not in ["gpt-4o-mini"]:
            raise ValueError("Invalid model selection")
        if not tone.strip():
            raise ValueError("Tone cannot be empty")
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
        if base_prompt_type not in PREDEFINED_PROMPTS:
            raise ValueError("Invalid prompt type selection")

        base_default_prompt = PREDEFINED_PROMPTS[base_prompt_type]

        # Check if settings already exist for the user
        result = await session.execute(
            select(Setting).where(Setting.user_id == user.id)
        )
        existing_settings = result.scalar_one_or_none()
        print(f"Debug: existing_settings type: {type(existing_settings)}")

        if existing_settings:
            print("Debug: Updating existing settings")
            existing_settings.model = model
            existing_settings.tone = tone
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
                model = model,
                tone = tone,
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
        # Debug print to check final settings type (either updated or newly created)
        print("Debug: Settings saved successfully for user", user.id)
        return RedirectResponse(url = "/dashboard", status_code = 303)
    except ValueError as e:
        print(f"Validation error: {str(e)}")
        return templates.TemplateResponse("settings.html", {
            "request": request,
            "error": str(e),
            "predefined_prompts": PREDEFINED_PROMPTS
        })
    except Exception as e:
        print(f"Error saving settings: {str(e)}")
        raise HTTPException(status_code = 500, detail = "Settings save failed")
