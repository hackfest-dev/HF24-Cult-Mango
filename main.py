import random

from pydantic import BaseModel, Field

from api.db import DBApi
from api.llm import OpenAIChatAgent
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

    def insertion(self, query_txt: str, ingredient: str, tags: list[str]):
        metadata = {'ingredient': ingredient}

        for i in range(0, len(tags)): metadata[tags[i]] = True

        self.chromadb.add(
            ids="".join(random.choices(DBApiExt.CHARS, k=8)),
            documents=query_txt,
            metadatas=metadata
        )


class OpenAIChatAgentExt(OpenAIChatAgent):
    class Ingredients(BaseModel):
        product_name: str = Field(..., description="The name of the product")
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
            # seed=1234,
        )
        response = response.choices[0].message.content
        try:
            return self.Ingredients.parse_raw(response)
        except SyntaxError:
            return self.Ingredients(product_name="Error", ingredients=[])
