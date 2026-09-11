import chromadb

from app.config import settings


chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)


def get_collection():
    return chroma_client.get_or_create_collection(name=settings.COLLECTION_NAME)


def reset_collection():
    try:
        chroma_client.delete_collection(name=settings.COLLECTION_NAME)
    except Exception:
        pass
    return chroma_client.create_collection(name=settings.COLLECTION_NAME)
