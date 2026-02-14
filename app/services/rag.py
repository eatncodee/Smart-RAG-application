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
            description="""Search the internal knowledge base for specific factual information.

USE this function ONLY when the user asks about:

📊 Company/Organization Information:
- Financial data (revenue, growth, metrics, budgets)
- Employee count, team structure, hiring information
- Products, services, features, or offerings
- Policies, procedures, guidelines, or documentation
- Office locations, company history, founding details
- Leadership (CEO, executives, managers)

👤 Personal Information (from uploaded resumes/documents):
- Education background, degrees, universities
- Work experience, job history, previous roles
- Skills, certifications, qualifications
- Projects, achievements, publications
- Contact information, languages spoken
- Any biographical or professional details about individuals mentioned in uploaded documents

📄 Document Content:
- Specific facts, dates, or details from uploaded files
- Quotes or excerpts from documents
- Technical specifications or requirements
- Meeting notes, action items, decisions

DO NOT use this function for:

❌ General Knowledge:
- Math calculations (2+2, 50*30, etc.)
- Scientific facts (photosynthesis, gravity, etc.)
- Historical events (World War II, etc.)
- Geography (capitals, countries, etc.)
- Common definitions or explanations

❌ Creative Tasks:
- Writing stories, poems, or code
- Brainstorming ideas
- Giving opinions or advice (unless based on uploaded documents)

❌ Conversational:
- Greetings (Hi, Hello, How are you)
- Casual chat
- Clarification questions

🎯 Decision Rule:
If the answer could be in an uploaded document or company knowledge base → SEARCH
If the answer is general knowledge or conversational → DO NOT SEARCH

Examples that NEED search:
✅ "What was our Q4 revenue?"
✅ "What is Rudraksh's educational background?"
✅ "What skills does the uploaded resume mention?"
✅ "How many employees do we have?"
✅ "What projects has the person worked on?"
✅ "What is mentioned about Python in the documents?"

Examples that DON'T need search:
❌ "What is 2+2?"
❌ "Explain what Python is"
❌ "What's the capital of France?"
❌ "Write a function to sort an array"
❌ "Hello, how are you?"
❌ "Can you help me?"
""",
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

def chat_with_function_calling(user_message: str, conversation_history:list | None = None) -> dict:
    if conversation_history is None:
        conversation_history = []
    conversation_history.append({"role": "user","parts": [{"text":user_message}]})   
    system_instruction = """You are a helpful AI assistant with access to a company knowledge base.

IMPORTANT: You have TWO capabilities that work together:

1. GENERAL KNOWLEDGE (Your Training):
   - Answer math, science, history, geography, coding questions
   - Provide explanations, definitions, how-to guides
   - Have casual conversations, greetings
   - Example: "What is 2+2?" → Answer: "4"
   - Example: "What's the capital of Haryana?" → Answer: "Chandigarh"
   - Example: "Explain Python" → Answer: [Explanation from your knowledge]

2. KNOWLEDGE BASE SEARCH (Uploaded Documents):
   - Search when asked about specific company/personal information
   - Use the search_documents function for uploaded resume/document questions
   - Example: "What's in the resume?" → [Search and answer]
   - Example: "What was our Q4 revenue?" → [Search and answer]

DECISION RULE:
- Can you answer from general knowledge? → Answer directly (no search)
- Is it asking about uploaded documents/company data? → Use search_documents
- Not sure? → Prefer answering directly if it's common knowledge

You are capable and knowledgeable. Don't refuse to help with general questions!
"""
    try:
        response = client.models.generate_content(model=settings.CHAT_MODEL,contents=conversation_history,config=types.GenerateContentConfig(tools=[search_tool],temperature=0.7,system_instruction=system_instruction))

        function_calls = []

        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if part.function_call:
                    function_calls.append(part.function_call)


        if function_calls:
            for fc in function_calls:
                if fc.name == "search_documents":
                    query = fc.args.get("query","")
                    search_results = search_documents(query)
                    conversation_history.append({"role": "model","parts": [{"function_call": fc}]})
                    conversation_history.append({"role": "user","parts": [{"function_response": {"name": "search_documents","response": {"result": search_results}}}]}) 

            final_response = client.models.generate_content(model=settings.CHAT_MODEL,contents=conversation_history,config=types.GenerateContentConfig(temperature=0.7,system_instruction=system_instruction))
            
            answer = final_response.text
            used_rag = True
        
        else:
            answer = response.text
            used_rag = False
        
        conversation_history.append({"role": "model","parts": [{"text":answer}]})
            
        return {
            "answer": answer,
            "used_rag": used_rag,
            "conversation_history": conversation_history
        }
    except Exception as e:
        error_message = f"I encountered an error: {str(e)}"
        
        conversation_history.append({
            "role": "model",
            "parts": [{"text": error_message}]
        })
        
        return {
            "answer": error_message,
            "used_rag": False,
            "conversation_history": conversation_history,
            "error": str(e)
        }

def generate_answer(question :str ,context_docs: str):
    context="\n".join(context_docs)
    prompt = f"""You are a helpful assistant answering questions.
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
        