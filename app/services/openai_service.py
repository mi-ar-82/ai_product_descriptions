# File: app/services/openai_service.py
import openai
from app.config import settings
from app.services.image_processing import process_image


openai.api_key = settings.OPENAI_API_KEY


async def generate_product_description(messages: list, model: str, temperature: float, max_tokens: int, use_base64_image: bool) -> str:
    try:
        print(f"Debug: Calling OpenAI API with model: {model}")
        print(f"Debug: Temperature: {temperature}, max_tokens: {max_tokens}")
        print(f"Debug: Using base64 image: {use_base64_image}")

        if use_base64_image:
            for message in messages:
                if isinstance(message['content'], list):
                    for content in message['content']:
                        if content['type'] == 'image_url':
                            content['image_url']['url'] = process_image(content['image_url']['url'])

        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        print("Debug: OpenAI API response:", response)
        print("Debug: Data type of response:", type(response))

        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        raise e
