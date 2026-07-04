"""
MI AI - Image Generation
Pollinations AI use karta hai (free, koi API key nahi chahiye)
"""

import requests
import urllib.parse
import os
import time
from config import POLLINATIONS_IMAGE_URL, POLLINATIONS_PARAMS, TEMP_DIR


def generate_image(prompt: str) -> str:
    """
    Prompt se image generate karta hai aur local file path return karta hai.
    Fail hone par None return karega.
    """
    encoded_prompt = urllib.parse.quote(prompt)
    url = POLLINATIONS_IMAGE_URL.format(prompt=encoded_prompt) + POLLINATIONS_PARAMS

    try:
        response = requests.get(url, timeout=60)
        response.raise_for_status()

        filename = f"image_{int(time.time())}.jpg"
        filepath = os.path.join(TEMP_DIR, filename)

        with open(filepath, "wb") as f:
            f.write(response.content)

        return filepath
    except Exception as e:
        print(f"Image generation error: {e}")
        return None