from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.rag import ask_question

router = APIRouter(prefix="/chat", tags=["chat"])

class Question(BaseModel):
    question: str
    n_results: int = 3  
    
class ChatResponse(BaseModel):
    question: str
    answer: str


@router.post("/ask", response_model=ChatResponse)
async def ask(q: Question):
    try:
        result = ask_question(q.question, q.n_results)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))