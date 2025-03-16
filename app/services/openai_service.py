# File: app/services/openai_service.py
import openai
from app.config import settings

openai.api_key = settings.OPENAI_API_KEY


async def generate_product_description(messages: list, model: str, temperature: float, max_tokens: int) -> str:
    try:
        print(f"Debug: Calling OpenAI API with model: {model}")
        print(f"Debug: Temperature: {temperature}, max_tokens: {max_tokens}")

        response = openai.ChatCompletion.create(
            model = model,
            messages = messages,
            temperature = temperature,
            max_tokens = max_tokens,
        )
        print("Debug: OpenAI API response received")
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        raise e
