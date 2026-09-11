# 🎙️ Real-Time Voice Assistant with RAG

### A full-duplex voice AI system that lets you have a natural spoken conversation with your documents.
#### Built with FastAPI · Gemini · Sarvam AI · Cartesia Sonic-3

---

## Deploy on Render

This repository now includes a Render Blueprint in `render.yaml` and a production dependency file in `requirements.txt`.

1. Push the repository to GitHub and create a new **Blueprint** in the [Render Dashboard](https://dashboard.render.com/).
2. Select this repository. Render will use `render.yaml` to create one Python Web Service.
3. When prompted, enter these secret environment variables:
   - `GOOGLE_API_KEY` — Gemini/Google AI key for chat and embeddings
   - `SARVAM_API_KEY` — Sarvam AI speech-to-text key
   - `CARTESIA_API_KEY` — Cartesia text-to-speech key
4. After the deploy finishes, open the service URL. The voice UI is served at `/` and `/voice`; the REST chat UI is available at `/chat`.
5. The health check is available at `/health`; API documentation is available at `/docs`.

The service must remain a **Web Service**, not a Static Site, because the voice assistant uses an inbound WebSocket at `/ws/voice/{userId}`. The frontend automatically uses `wss://` when the deployed page is served over HTTPS.

### ChromaDB persistence

The default Blueprint uses `./chroma_db`, which is suitable for a demo but is on Render's ephemeral filesystem. Uploaded documents can disappear after a restart or deploy. For persistent documents, attach a paid Render persistent disk mounted at `/var/data` and set:

```text
CHROMA_DB_PATH=/var/data/chroma_db
```

Alternatively, replace local ChromaDB with a hosted vector database before production use.

### Local run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open `http://localhost:8000/`.

---

## The Problem with Most Voice Bots

They follow a rigid loop — listen → think → speak → repeat. You have to wait for the bot to finish before you can say anything. It feels robotic.

This system runs all three in parallel. While the AI is speaking, it is already listening. Interrupt it mid-sentence and it immediately drops what it was saying, processes your new input, and responds — like a real conversation.

---

## 🎥 Demo
![Project Demo](app/demo/GIF_demo.gif)

### Full walkthrough video (with sound):
<video src="https://github.com/user-attachments/assets/3807d2d7-48f9-44b1-bc6a-f7366b1ec7a0" width="100%" controls>
</video>

---

## ✨ Key Features

- 🗣️ **Full-Duplex Voice Interaction** — Persistent, two-way audio streaming via WebSockets. The system listens even while it is speaking, creating a truly fluid conversation loop.

- 🧠 **Intelligent Decision Making** — Powered by Gemini with native Tool Calling. Autonomously decides per query whether to search your documents via ChromaDB or answer from general knowledge.

- 🚫 **Real-Time Barge-in** — An `asyncio.Event` kill-switch instantly terminates the active TTS stream the moment your voice is detected, letting you interrupt naturally.

- ⚡ **Parallel Pipeline Architecture** — STT, LLM, and TTS run in a pipelined fashion. The AI starts speaking the first sentence while the rest of the response is still being generated.
  - 🦻 **Ear** (Sarvam AI) — `saarika:v2.5` for multilingual speech recognition with auto language detection
  - 🧠 **Brain** (Gemini) — Tool calling + ChromaDB RAG for document-grounded answers
  - 🔊 **Mouth** (Cartesia) — `sonic-3` for realistic 44.1kHz streaming audio

- 📜 **Persistent Context Memory** — Conversation history survives interruptions. Ask follow-ups like *"Wait, go back to what you said before"* and it will know.

- 📥 **Seamless Document Ingestion** — Upload PDFs and they are automatically chunked, embedded with `gemini-embedding-001`, and stored in ChromaDB for instant retrieval.

---



## 🏗️ How It Works

```
Browser Mic
    │  Int16 PCM @ 16kHz
    ▼
Custom VAD (SilenceDetector)
    │  triggers after 0.8s silence
    ▼
Sarvam AI STT  →  Gemini  →  Cartesia TTS
  saarika:v2.5     tool calling     sonic-3
  auto language    ChromaDB RAG     pcm_f32le @ 44.1kHz
                       │
    ◄──────────────────┘
    audio chunks stream back as they are generated
    browser plays first chunk before full response is done
```

**🦻 Ear** — `SilenceDetector` runs RMS volume analysis on every incoming PCM chunk. Triggers after 0.8 seconds of post-speech silence.

**🧠 Brain** — Gemini with tool calling. Decides per query whether to search ChromaDB or answer from general knowledge. Full conversation history passed every turn.

**🔊 Mouth** — Cartesia WebSocket stays persistent across sentences. Text is split into sentences and streamed in — first audio chunk arrives before the full response is generated.

---

## 🚫 Barge-in

The moment your voice is detected while the AI is speaking, an `asyncio.Event` kill switch fires — cancelling the active TTS stream instantly and returning to listening.

```python
async for audio_chunk in text_to_speech(response):
    if barge_in_event.is_set():
        break  # drop everything, go back to listening
    await websocket.send_bytes(audio_chunk)
```

---

## 🛠️ Tech Stack

| Layer | Technology | Model |
|---|---|---|
| Backend | FastAPI + Python 3.14 | — |
| STT | Sarvam AI | `saarika:v2.5` |
| LLM | Google Gemini | `gemini-2.5-flash` |
| Embeddings | Google Gemini | `gemini-embedding-001` |
| TTS | Cartesia | `sonic-3` |
| Vector DB | ChromaDB | Local persistent |
| Concurrency | asyncio | Parallel pipeline |
| Frontend | Web Audio API | — |

---

## ⚡ Latency

| Stage | Typical |
|---|---|
| VAD trigger | < 50ms |
| Sarvam STT | 400–700ms |
| Gemini first token | 500–900ms |
| Cartesia first audio chunk | < 100ms |
| **Time to first audio** | **~2–3 seconds** |

---

## 📁 Project Structure

```
├── app/
│   ├── demo/
│   │   ├── GIF_demo.gif      # High-speed barge-in preview
│   │   └── Video.mp4         # Raw demo recording
│   ├── frontend/
│   │   ├── chat.html         # Standard chat interface
│   │   └── voice.html        # Voice-enabled Web Audio interface
│   ├── routes/
│   │   ├── chat.py           # REST endpoints
│   │   ├── documents.py      # PDF upload & ingestion logic
│   │   └── voice.py          # WebSocket & VAD pipeline
│   └── services/
│       ├── rag.py            # Gemini + tool calling logic
│       ├── streaming.py      # Async stream handlers
│       ├── embedding.py      # Gemini embeddings
│       └── database.py       # ChromaDB connection & management
├── audio/
│   ├── audio_convert.py      # Sample rate & format conversion
│   ├── audio_play.py         # Local playback utilities
│   └── record_audio.py       # CLI recording for testing
├── .env                      # API Keys (Gemini, Sarvam, Cartesia)
├── requirements.txt          # Project dependencies
├── render.yaml               # Render Blueprint
└── README.md                 # Project documentation
```
