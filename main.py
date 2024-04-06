import random

import streamlit
from pydantic import BaseModel, Field

from api.db import DBApi
from api.llm import OpenAIChatAgent
from api.search import search
from firebase_admin import firestore


class DBApiExt(DBApi):
    CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"

    def __init__(self, secrets):
        super().__init__(secrets)
        self.preferences = self.firestore.collection("preferences")

    def add_preference(self, preference):
        prefs = self.preferences.where(
            filter=firestore.FieldFilter(u'user', u'==', self.user.reference)
        ).get()
        if not prefs:
            self.preferences.add({"user": self.user.reference, "preferences": [preference]})
            return
        prefs = prefs[0].reference
        prefs.update({"preferences": firestore.ArrayUnion([preference])})

    def remove_preference(self, preference):
        prefs = self.preferences.where(
            filter=firestore.FieldFilter(u'user', u'==', self.user.reference)
        ).get()
        if not prefs: return
        prefs = prefs[0].reference
        prefs.update({"preferences": firestore.ArrayRemove([preference])})

    def get_preferences(self):
        prefs = self.preferences.where(
            filter=firestore.FieldFilter(u'user', u'==', self.user.reference)
        ).get()
        return prefs[0].get("preferences") if prefs else []

    def fetch(self, ingredient: str, **tags):
        ingredient = ingredient.lower().strip()
        info = self.chromadb.get(ids=ingredient, limit=1)["documents"]
        if info: return info[0]
        info = search(ingredient)
        tags.update(ingredient=ingredient)
        self.chromadb.add(
            ids=ingredient,
            documents=info,
            metadatas=tags,
        )
        return info


class OpenAIChatAgentExt(OpenAIChatAgent):
    class Ingredients(BaseModel):
        product_name: str = Field(..., description="The name of the product", max_length=16)
        ingredients: list[str] = Field(..., description="The ingredients of the product")

    def process_raw_ocr(self, raw_ocr: str) -> Ingredients:
        response = self.client.chat.completions.create(
            model="mistralai/Mistral-7B-Instruct-v0.1",
            response_format={
                "type": "json_object",
                "schema": self.Ingredients.model_json_schema()
            },
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert analyst designed to output JSON data. "
                               "You will carefully read the raw OCR data and output the list of individual ingredients."
                },
                {
                    "role": "user",
                    "content": raw_ocr
                },
            ],
            temperature=0.6,
            seed=1234,
        )
        response = response.choices[0].message.content
        try:
            return self.Ingredients.parse_raw(response)
        except SyntaxError:
            return self.Ingredients(product_name="Error", ingredients=[])
