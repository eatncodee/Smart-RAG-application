import asyncio
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.config import settings
from app.routes import chat, documents, voice
from app.services.rag import search_documents


FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"

app = FastAPI(
    title="Real-Time Full-Duplex Voice RAG Assistant",
    description="Streaming voice RAG assistant using FastAPI, Gemini, Sarvam AI, Cartesia, and ChromaDB.",
    version="3.1.1",
)

# Same-origin deployment does not need CORS, but this keeps the API usable from
# an optional separate frontend. Do not use credentials with a wildcard origin.
allow_all_origins = settings.CORS_ORIGINS == ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=not allow_all_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(voice.router)


@app.on_event("startup")
async def startup_event():
    # Avoid a paid embedding/API call on every Render restart unless explicitly
    # requested. Chroma is initialized by the service modules during import.
    if not settings.WARMUP_ON_STARTUP:
        print("ℹ️ Startup warmup disabled (set WARMUP_ON_STARTUP=true to enable).")
        return

    print("🔥 Warming up Vector Database and Embedding Models...")
    try:
        await asyncio.to_thread(search_documents, "initialization test")
        print("✅ Database warmed up and ready!")
    except Exception as exc:
        print(f"⚠️ Warmup failed, but server will continue: {exc}")


@app.get("/", include_in_schema=False)
async def frontend():
    """Serve the voice UI from the same origin as the WebSocket endpoint."""
    return FileResponse(FRONTEND_DIR / "voice.html", media_type="text/html")


@app.get("/voice", include_in_schema=False)
async def voice_frontend():
    return FileResponse(FRONTEND_DIR / "voice.html", media_type="text/html")


@app.get("/chat", include_in_schema=False)
async def chat_frontend():
    return FileResponse(FRONTEND_DIR / "chat.html", media_type="text/html")


@app.get("/api")
async def api_root():
    return {
        "message": "RAG API is running",
        "endpoints": {
            "upload": "POST /documents/upload",
            "ask": "POST /chat/ask",
            "list": "GET /documents/list",
            "chat_ui": "GET /chat",
            "voice_websocket": "GET /ws/voice/{userId}",
        },
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}
