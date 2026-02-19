from google import genai
from google.genai import types
from app.config import settings
from app.database import get_collection
from app.services.embedding import create_embedding
from app.services.rag import search_tool, search_documents

client = genai.Client(api_key=settings.GOOGLE_API_KEY)

async def stream_rag_response(user_message: str,conversation_history: list | None = None,websocket = None ):
    if conversation_history is None:
        conversation_history = []
    
    conversation_history.append({
        "role": "user",
        "parts": [{"text": user_message}]
    })
    
    system_instruction = """You are a helpful AI assistant with access to a company knowledge base.
IMPORTANT: You have TWO capabilities:
1. GENERAL KNOWLEDGE - Answer from your training:
   ✓ Math, science, history, geography
   ✓ Programming concepts and explanations
   ✓ Common knowledge questions
2. KNOWLEDGE BASE - Search uploaded documents:
   ✓ Company-specific information
   ✓ Resume/personal details
   ✓ Document content
RULE: Answer directly if it's general knowledge. Only search for specific document/company info.
"""
    try:
        if websocket:
            await websocket.send_json({
                "type": "status",
                "message": "Processing your question..."
            })
        response = client.models.generate_content_stream(
            model=settings.CHAT_MODEL,
            contents=conversation_history,
            config=types.GenerateContentConfig(
                tools=[search_tool],
                temperature=0.7,
                system_instruction=system_instruction
            )
        )  
        model_parts = []
        function_calls = []
        full_answer=""
        used_rag = False
        for chunk in response:
            if (chunk.candidates and chunk.candidates[0].content and 
                chunk.candidates[0].content.parts):
                for part in chunk.candidates[0].content.parts:
                    model_parts.append(part)
                    if hasattr(part, 'function_call') and part.function_call:
                        function_calls.append(part.function_call)
            
                if function_calls:
                    break
                if chunk.text:
                    full_answer += chunk.text
                if websocket:
                    await websocket.send_json({"type": "answer", "chunk": chunk.text})

        answer = full_answer
        
        if function_calls:
            used_rag = True
            
            if websocket:
                await websocket.send_json({
                    "type": "status",
                    "message": "🔍 Searching documents..."
                })

            conversation_history.append({
                        "role": "model", 
                        "parts": model_parts  
                    })
            function_responses = []
            for fc in function_calls:
                if fc.name == "search_documents":
                    query = fc.args.get("query", "")
                    search_results = search_documents(query)
                
                    function_responses.append({
                        "function_response": {
                            "name": "search_documents",
                            "response": {"result": search_results}
                        }
                    })

            conversation_history.append({
                "role": "user",
                "parts": function_responses
            })
            if websocket:
                await websocket.send_json({
                    "type": "status",
                    "message": "✨ Generating answer..."
                })
            
            response_stream = client.models.generate_content_stream(model=settings.CHAT_MODEL,contents=conversation_history,config=types.GenerateContentConfig(temperature=0.7,system_instruction=system_instruction))
            
            full_answer = ""
            for chunk in response_stream:
                if chunk.text:
                    full_answer += chunk.text
                    
                    if websocket:
                        await websocket.send_json({
                            "type": "answer",
                            "chunk": chunk.text
                        })
            
            answer = full_answer
        
        conversation_history.append({
            "role": "model",
            "parts": [{"text": answer}]
        })
        
        if websocket:
            await websocket.send_json({
                "type": "done",
                "used_rag": used_rag,
                "conversation_history": conversation_history
            })
        
        return {
            "answer": answer,
            "used_rag": used_rag,
            "conversation_history": conversation_history
        }
    
    except Exception as e:
        error_message = f"Error: {str(e)}"
        
        if websocket:
            await websocket.send_json({
                "type": "error",
                "message": error_message
            })
        
        return {
            "answer": error_message,
            "used_rag": False,
            "error": str(e)
        }