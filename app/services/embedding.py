from google import genai
import chromadb
from app.config import settings


client=genai.Client(api_key=settings.GOOGLE_API_KEY)

chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
collection = chroma_client.get_collection(name=settings.COLLECTION_NAME)


def create_embedding(text: str):
    result = client.models.embed_content(model=settings.EMBEDDING_MODEL,contents=text)
    if result.embeddings:
        return result.embeddings[0].values
    raise ValueError("The API returned no embeddings.")

def create_embeddings_batch(texts: list[str]):
    result=client.models.embed_content(model=settings.EMBEDDING_MODEL,contents=texts)
    if result and result.embeddings:
        embeddings = []
        for e in result.embeddings:
            if e.values is not None:
                embeddings.append([float(v) for v in e.values])
        return embeddings
    return None

