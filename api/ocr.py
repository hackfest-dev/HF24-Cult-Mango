import requests
import re

API_URL = "https://api-inference.huggingface.co/models/jinhybr/OCR-Donut-CORD"
headers = {"Authorization": "Bearer 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"}


def conv_xml(gen_text):
    gen_text = re.sub(r'<[^>]+>', '', gen_text)
    return gen_text


def ocr(image):
    image.save(".ocr.temp.png")
    with open(".ocr.temp.png", "rb") as image_file: data = image_file.read()
    response = requests.post(API_URL, headers=headers, data=data).json()[0]
    return conv_xml(response["generated_text"])


__all__ = [
    "ocr",
]
