from openai import AsyncOpenAI
from app.config import settings
from app.services.image_processing import process_image
from app.services.prompt_service import prompt_service
from app.services.ai_response_service import ai_response_service
from app.services.text_utils import convert_html_to_plain_text

client = AsyncOpenAI(api_key = settings.OPENAI_API_KEY)


async def generate_product_description(
        product_info: dict,
        ai_model: str,
        temperature: float,
        max_tokens: int,
        prompt_type: str = "conversion",
        use_base64_image: bool = False
) -> dict:
    try:
        print(f"Debug: Generating description with prompt type: {prompt_type}")
        print(f"Debug: Model: {ai_model}, Temperature: {temperature}, max_tokens: {max_tokens}")

        # Convert input_body from HTML to plain text
        plain_text_description = convert_html_to_plain_text(product_info['description'])
        # Update product_info with plain text description
        product_info['description'] = plain_text_description


        # Get prompt data
        prompt_data = prompt_service.get_prompt(prompt_type)

        # Format prompt for OpenAI API
        messages = prompt_service.format_prompt_for_api(
            prompt_data = prompt_data,
            product_info = product_info,
            api_type = "openai"
        )

        # Ensure 'json' is mentioned in messages when using json_object response format
        json_mentioned = False
        for message in messages:
            if isinstance(message["content"], str) and "json" in message["content"].lower():
                json_mentioned = True
                break
            elif isinstance(message["content"], list):
                for content_item in message["content"]:
                    if isinstance(content_item, dict) and content_item.get(
                            "type") == "text" and "json" in content_item.get("text", "").lower():
                        json_mentioned = True
                        break

        # If 'json' not mentioned, add it to the first text content
        if not json_mentioned:
            print("Debug: Adding JSON mention to message content")
            for message in messages:
                if isinstance(message["content"], list):
                    for content_item in message["content"]:
                        if isinstance(content_item, dict) and content_item.get("type") == "text":
                            content_item["text"] = content_item["text"] + " Please provide the response in JSON format."
                            json_mentioned = True
                            break
                    if json_mentioned:
                        break
                elif isinstance(message["content"], str):
                    message["content"] = message["content"] + " Please provide the response in JSON format."
                    json_mentioned = True
                    break

        # Process image if needed
        if use_base64_image and product_info.get("image_url"):
            for message in messages:
                if isinstance(message["content"], list):
                    for content in message["content"]:
                        if content.get("type") == "image_url":
                            base64_image = process_image(content["image_url"]["url"])
                            content["image_url"]["url"] = base64_image
                            print(f"Debug: Base64 image (first 100 chars): {base64_image[:200]}...")

        print(f"Debug: Message type: {type(messages)}")
        print(f"Debug: JSON mentioned in messages: {json_mentioned}")

        # Call OpenAI API
        response = await client.chat.completions.create(
            model = ai_model,
            messages = messages,
            temperature = temperature,
            max_tokens = max_tokens,
            response_format = {"type": "json_object"}
        )


        print(f"Debug: ai response = {response} ")
        print(f"Debug: response type: {type(response)}")




        raw_response = response.choices[0].message.content.strip()

        print(f"Debug: raw_response = {raw_response} ")
        print(f"Debug: Raw response type: {type(raw_response)}")

        # Parse structured response
        parsed_response = ai_response_service.parse_ai_response(raw_response)
        print(f"Debug: parsed_response = {parsed_response}")

        return parsed_response

    except Exception as e:
        print(f"OpenAI API Error: {e}")
        raise e
