import string
import random
import chromadb

chromadb_client = chromadb.PersistentClient(path="D:\Hackfest")

def insertion(query_txt, ingredient, tags):
    collection = chromadb_client.get_or_create_collection(name="data")
    meta_data = {'ingredient': ingredient}

    for i in range(0, len(tags)):
        meta_data[tags[i]] = True

    collection.add(
        ids=''.join([random.choice(string.ascii_letters.upper()) for n in range(3)]),
        documents=query_txt,
        metadatas=meta_data
    )
