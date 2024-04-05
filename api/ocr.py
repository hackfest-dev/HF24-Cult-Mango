import numpy as np
import requests

API_URL = "https://api-inference.huggingface.co/models/jinhybr/OCR-Donut-CORD"
headers = {"Authorization": "Bearer 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"}

def ocr(image):
    image.save("temp_ocr2.png")
    with open("temp_ocr2.png", "rb") as image_file: data = image_file.read()
    response = requests.post(API_URL, headers=headers, data=data).json()
    return " ".join(r["generated_text"] for r in response)

__all__ = [
    "ocr",
]
