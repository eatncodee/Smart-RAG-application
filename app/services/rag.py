from google import genai
from google.genai import types
from app.config import settings
from app.db import get_collection
from app.services.embedding import create_embedding,create_embeddings_batch


client = genai.Client(api_key=settings.GOOGLE_API_KEY)


search_tool = types.Tool(
    function_declarations=[
        types.FunctionDeclaration(
            name="search_documents",
            description="Search the knowledge base for relevant information. Use this when you need specific information about the company, products, employees, revenue, or any other stored data.",
            parameters=types.Schema(
                type=types.Type.OBJECT,
                properties={
                    "query": types.Schema(
                        type=types.Type.STRING,
                        description="The search query to find relevant documents"
                    )
                },
                required=["query"]
            )
        )
    ]
)


def search_documents(question: str)-> str:
    collection = get_collection()
    
    q_emb = create_embedding(question)
    if q_emb:
        results = collection.query(
            query_embeddings=[q_emb],
            n_results=3
        )
        
        if results['documents'] and len(results['documents']) > 0:
            docs=results['documents'][0]
            return "\n\n".join(docs)
    return "No relevant docs found"

# def chat_with_function_calling(user_message: str, conversation_history:list | None = None) -> dict:
#     if conversation_history is None:
#         conversation_history = []

#     conversation_history.append({
#         "role": "user",
#         "parts": [user_message]
#     })    

#     response = client.models.generate_content(
#         model=settings.CHAT_MODEL,
#         contents=conversation_history,
#         config=types.GenerateContentConfig(tools=[search_tool],temperature=0.7)
#     )
#     function_calls = []
#     if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
#         for part in response.candidates[0].content.parts:
#             if part.function_call:
#                 function_calls.append(part.function_call)


#     if function_calls:
#         for fc in function_calls:
#             if fc.name == "search_documents":
#                 query = fc.args["query"]
#                 search_results = search_documents(query)

#     conversation_history.append({
#         "role": "model",
#         "parts": [{"function_call": fc}]
#     })

#     conversation_history.append({
#         "role": "user",
#         "parts": [{
#             "function_response": {
#                 "name": "search_documents",
#                 "response": {"result": search_results}
#             }
#         }]
#     })

def generate_answer(question :str ,context_docs: str):
    context="\n".join(context_docs)
    prompt = f"""You are a helpful assistant answering questions about a company.
            Context (retrieved information):
            {context}

            Question: {question}

            Instructions:
            - Keep the answer concise and direct

            Answer:"""
    response = client.models.generate_content(model=settings.CHAT_MODEL,contents=prompt)
    return response.text


def ask_question(question: str, n_results: int = 3) -> dict:
    retrieved_docs = search_documents(question)
    if not retrieved_docs:
        return {
            'question': question,
            'answer': "I don't have any documents to answer your question. Please upload some documents first.",
            'sources': []
        }
    
    answer = generate_answer(question, retrieved_docs)
    
    return {
        'question': question,
        'answer': answer,
    }
        