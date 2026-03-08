# Smart RAG API with Agentic Tool Calling 🧠🤖

A high-performance **Agentic RAG (Retrieval-Augmented Generation)** system built using **FastAPI**, **ChromaDB**, and the **Google Gemini SDK**.

Unlike standard RAG pipelines, this application uses **Tool Calling** to act as a decision-maker. It intelligently decides whether to search local documents for context or answer from general knowledge, optimizing both cost and accuracy.

## 🎥 Demo

![Project Demo](app/demo/gif_demo.gif)
*Watch the agent intelligently switch between general chat and document retrieval.*

### Watch the full video (with sound):
https://github.com/user-attachments/assets/4f414d16-d233-4cb9-98b9-c2432d29c3ab


---


## ✨ Key Features

- **Smart Retrieval (Agentic RAG):** The LLM acts as an autonomous agent. It only triggers a document search when it identifies a specific need for local knowledge.
- **Streaming Responses:** Implements real-time token streaming using `generate_content_stream` for a smooth, "ChatGPT-like" user experience.
- **WebSocket Integration:** Supports persistent, two-way communication for seamless real-time chat interactions.
- **Automated Document Ingestion:** Upload PDFs via Postman or the frontend; the system automatically chunks, embeds, and stores them in ChromaDB.
- **Type-Safe Implementation:** Built with the latest **google-genai SDK**, utilizing Pydantic for strict schema validation and robustness.

## 🛠️ Tech Stack

- **Backend:** FastAPI (Python 3.12+)
- **LLM:** Google Gemini SDK
- **Vector Database:** ChromaDB
- **Frontend:** HTML, JavaScript
- **Tools:** Uvicorn, Pydantic, Python-Multipart