import firebase_admin
import chromadb
from firebase_admin import credentials, firestore
from google.cloud.firestore_v1.base_query import FieldFilter  # noqa


class DBApi:
    def __init__(self, secrets):
        self.firestore = self.get_firestore(secrets)
        self.chromadb = self.get_chromadb(secrets)
        self.users = self.firestore.collection("users")
        self.user = None

    @staticmethod
    def get_firestore(secrets):
        cred = credentials.Certificate(secrets["FIREBASE_CREDENTIALS"])
        firebase_admin.initialize_app(cred)
        return firestore.client()

    @staticmethod
    def get_chromadb(secrets):
        return chromadb.PersistentClient("vecdb").get_or_create_collection(secrets["CHROMADB_COLLECTION"])

    def auth(self, username, password):
        user = self.users.where(filter=FieldFilter(u'username', u'==', username)).where(
            filter=FieldFilter(u'password', u'==', password)).get()
        if user and user[0].exists: self.user = user[0]
        return self.user
