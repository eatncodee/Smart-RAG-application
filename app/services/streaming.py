from google import genai
from google.genai import types
from app.config import settings
from app.database import get_collection
from app.services.embedding import create_embedding
from app.services.rag import search_tool, search_documents

