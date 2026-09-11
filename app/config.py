from dotenv import load_dotenv
import os

load_dotenv()


def _first_env(*names: str) -> str | None:
    """Return the first non-empty environment variable in ``names``."""
    for name in names:
        value = os.getenv(name)
        if value:
            return value
    return None


class Settings:
    # The app uses Gemini's OpenAI-compatible endpoint for chat and the
    # Google GenAI SDK for embeddings. Keep the old ``key`` name as a
    # backwards-compatible local-development fallback.
    GOOGLE_API_KEY = _first_env("GOOGLE_API_KEY", "GEMINI_API_KEY", "key")
    OPENAI_API_KEY = GOOGLE_API_KEY  # backwards-compatible alias used by services

    SARVAM_API_KEY = _first_env("SARVAM_API_KEY", "Sarvam_key", "sarvam_key")
    CARTESIA_API_KEY = _first_env("CARTESIA_API_KEY", "Cartesia_key", "cartesia_key")

    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "models/gemini-embedding-001")
    CHAT_MODEL = os.getenv("CHAT_MODEL", "gemini-2.5-flash")

    # Set CHROMA_DB_PATH to a mounted Render disk path (for example
    # /var/data/chroma_db) when document persistence is required.
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "docs")

    _cors_origins = os.getenv("CORS_ORIGINS", "*")
    CORS_ORIGINS = [origin.strip() for origin in _cors_origins.split(",") if origin.strip()]
    WARMUP_ON_STARTUP = os.getenv("WARMUP_ON_STARTUP", "false").lower() == "true"


settings = Settings()
