Smart RAG API with Agentic Tool Calling
This is a high-performance, Agentic RAG (Retrieval-Augmented Generation) system built using FastAPI, ChromaDB, and Google Gemini SDK(Software development kit). 
Unlike standard RAG, this application uses Tool Calling to decide whether to search local documents or answer from general knowledge, optimizing both cost and accuracy.


:Key Features
-Smart Retrieval (Agentic RAG): The LLM acts as a decision-maker. It only triggers a document search when it identifies a need for specific local knowledge.
-Streaming Responses: Real-time token streaming using generate_content_stream for a smooth, ChatGPT-like user experience.
-WebSocket Integration: Supports persistent, two-way communication for real-time chat interactions.
-Automated Document Ingestion: Upload PDFs via Postman or the frontend; the system automatically chunks, embeds, and stores them in ChromaDB.
-Type-Safe Implementation: Built with the latest google-genai SDK using Pydantic for strict schema validation.


:Tech Stack
Backend: FastAPI (Python 3.12+)
LLM: Google Gemini SDK
Vector Database: ChromaDB
Frontend: [HTML,Javascript]
Tools: Uvicorn, Pydantic, Python-Multipart
