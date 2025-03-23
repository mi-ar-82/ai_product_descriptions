# File: app/services/openai_service.py
import openai
from app.config import settings
from app.services.image_processing import process_image


openai.api_key = settings.OPENAI_API_KEY


async def generate_product_description(
        messages: list, model: str, temperature: float, max_tokens: int, use_base64_image: bool) -> str:
    try:
        print(f"Debug: Calling OpenAI API with model: {model}")
        print(f"Debug: Temperature: {temperature}, max_tokens: {max_tokens}")
        print(f"Debug: Using base64 image: {use_base64_image}")

        if use_base64_image:
            for message in messages:
                if isinstance(message['content'], list):
                    for content in message['content']:
                        if content['type'] == 'image_url':
                            base64_image = process_image(content['image_url']['url'])
                            content['image_url']['url'] = base64_image
                            print(f"Debug: Base64 image (first 100 characters): {base64_image[:100]}...")

        # Create a copy of the messages to modify for printing
        print_messages = messages.copy()
        for message in print_messages:
            if isinstance(message['content'], list):
                for content in message['content']:
                    if content['type'] == 'image_url':
                        content['image_url']['url'] = content['image_url']['url'][:100] + "..."

        print("Debug: Full message being sent to OpenAI API (base64 image truncated):")
        print(print_messages)






        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        print("Debug: OpenAI API response:")
        print(response) #openai api output
        print("Debug: Data type of response:", type(response))

        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API Error: {e}")
        raise e
