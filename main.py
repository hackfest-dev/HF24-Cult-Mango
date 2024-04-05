import os
import random
import string

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


if __name__ == '__main__':
    db_api = DBApiExt(os.environ)
    db_api.auth("admin", "admin")
    db_api.remove_preference("vegan2")
