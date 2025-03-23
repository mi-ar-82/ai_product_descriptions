# app/services/image_processing.py

import requests
from PIL import Image
import io
import base64


def process_image(image_url):
    response = requests.get(image_url)
    img = Image.open(io.BytesIO(response.content))

    # Resize image
    img.thumbnail((512, 512))

    # Convert to PNG
    buffer = io.BytesIO()
    img.save(buffer, format = "PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/png;base64,{img_str}"


print("Debug: Image processing service initialized")
