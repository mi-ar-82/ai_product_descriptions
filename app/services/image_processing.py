# app/services/image_processing.py

import requests
from PIL import Image
import io
import base64
import binascii  # Missing import

def process_image(image_url):
    try:
        response = requests.get(image_url)
        img = Image.open(io.BytesIO(response.content))

        # Resize image
        img.thumbnail((512, 512))

        # Convert to PNG
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        base64_image = f"data:image/png;base64,{img_str}"

        # Validate before returning
        if not validate_base64(base64_image):
            raise ValueError("Invalid base64 image generated")

        print(f"Debug: Processed image to base64, first 30 chars: {base64_image[:30]}...")
        print(type(base64_image))
        return base64_image

    except Exception as e:
        print(f"Error processing image: {e}")
        raise e

def validate_base64(image_str: str) -> bool:
    """Validate if a string is properly formatted base64 image data."""
    try:
        # Check basic format
        if not image_str.startswith("data:image/"):
            return False

        # Split the data URI components
        header, data = image_str.split(",", 1)
        parts = header.split(";")

        # Validate mime type and encoding
        if len(parts) < 2 or parts[-1] != "base64":
            return False

        # Attempt to decode the base64 data
        base64.b64decode(data, validate=True)
        return True

    except (ValueError, binascii.Error) as e:
        print(f"Debug: Base64 validation failed: {str(e)}")
        return False
    except Exception as e:
        print(f"Error validating base64: {str(e)}")
        return False

print("Debug: Image processing service initialized")
