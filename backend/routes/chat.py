from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.ai_service import get_ai_response

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    reply = get_ai_response(request.message)
    return ChatResponse(reply=reply)
