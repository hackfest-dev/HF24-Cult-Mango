import cv2
import requests
import re
import easyocr
import numpy as np

API_URL = "https://api-inference.huggingface.co/models/jinhybr/OCR-Donut-CORD"
headers = {"Authorization": "Bearer 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"}


def conv_xml(gen_text):
    gen_text = re.sub(r'<[^>]+>', '', gen_text)
    return gen_text


def ocr(image):
    # image = cv2.imread(image)
    reader = easyocr.Reader(['en'])
    blocks = reader.readtext(image)
    extracted_text = ' '.join([text[1] for text in blocks])
    return extracted_text


__all__ = [
    "ocr",
]
