# File: app/services/openai_service.py
import openai
from app.config import settings

openai.api_key = settings.OPENAI_API_KEY

async def generate_product_description(prompt: str, model: str, temperature: float, max_tokens: int) -> str:
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        raise e
