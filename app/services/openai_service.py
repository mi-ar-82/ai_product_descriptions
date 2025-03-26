# File: app/services/openai_service.py
import openai
from app.config import settings
from app.services.image_processing import process_image
from app.services.prompt_service import prompt_service
from app.services.ai_response_service import ai_response_service

openai.api_key = settings.OPENAI_API_KEY


async def generate_product_description(
        product_info: dict,
        model: str,
        temperature: float,
        max_tokens: int,
        prompt_type: str = "conversion",
        use_base64_image: bool = False
) -> dict:
    try:
        print(f"Debug: Generating description with prompt type: {prompt_type}")
        print(f"Debug: Model: {model}, Temperature: {temperature}, max_tokens: {max_tokens}")

        # Get prompt data
        prompt_data = prompt_service.get_prompt(prompt_type)

        # Format prompt for OpenAI API
        messages = prompt_service.format_prompt_for_api(
            prompt_data = prompt_data,
            product_info = product_info,
            api_type = "openai"
        )

        # Process image if needed
        if use_base64_image and product_info.get("image_url"):
            for message in messages:
                if isinstance(message['content'], list):
                    for content in message['content']:
                        if content.get('type') == 'image_url':
                            base64_image = process_image(content['image_url']['url'])
                            content['image_url']['url'] = base64_image
                            print(f"Debug: Base64 image (first 100 chars): {base64_image[:100]}...")

        # Create debug-friendly version of messages
        print_messages = messages.copy()
        for message in print_messages:
            if isinstance(message['content'], list):
                for content in message['content']:
                    if content.get('type') == 'image_url':
                        content['image_url']['url'] = content['image_url']['url'][:100] + "..."

        print(f"Debug: Messages for OpenAI: {print_messages}")
        print(f"Debug: Message type: {type(messages)}")

        # Call OpenAI API
        response = openai.ChatCompletion.create(
            model = model,
            messages = messages,
            temperature = temperature,
            max_tokens = max_tokens,
        )

        raw_response = response.choices[0].message.content.strip()
        print(f"Debug: Raw response type: {type(raw_response)}")

        # Parse structured response
        parsed_response = prompt_service.parse_ai_response(raw_response)
        return parsed_response

    except Exception as e:
        print(f"OpenAI API Error: {e}")
        raise e
