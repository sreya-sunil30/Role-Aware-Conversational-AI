from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
from pathlib import Path
from backend.confidence import calculate_confidence
import time
from openai import OpenAI
from backend.config import SAFE_CONFIG, ALLOWED_MODELS

load_dotenv()

app = FastAPI()

analytics = {
    "total_messages": 0,
    "total_chats": 0,
    "feedback_up": 0,
    "feedback_down": 0
}
#API call
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


openai_client = OpenAI(api_key=OPENAI_API_KEY)


conversation_memory = {
    "general": [],
    "sap": [],
    "mentor": [],
    "coding": []
}


MAX_MEMORY = 6
last_role = None


SYSTEM_PROMPTS = {
    "general": "You are a helpful and friendly AI assistant.",
    "sap": "Answer as an SAP expert with real-world SAP examples.",
    "mentor": "Explain concepts step by step in a teaching and mentoring style.",
    "coding": "Answer as a professional software engineer with clean code."
}


class ChatRequest(BaseModel):
    message: str
    role: str = "general"
    provider: str = "groq"

class Feedback(BaseModel):
    value: str  

@app.post("/chat")
def chat(req: ChatRequest):
    global last_role


    role = req.role.lower().strip()
    if role not in SYSTEM_PROMPTS:
        role = "general"


    memory = conversation_memory[role]


    role_switched = False
    if last_role != role:
        role_switched = True
        last_role = role
        memory.clear()
        memory.append({
            "role": "system",
            "content": SYSTEM_PROMPTS[role]
        })


    if not memory:
        memory.append({
            "role": "system",
            "content": SYSTEM_PROMPTS[role]
        })


    memory.append({
        "role": "user",
        "content": req.message
    })


    start_time = time.time()

    if req.provider == "groq":
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {GROQ_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "llama-3.1-8b-instant",
                "messages": memory
            }
        )
        data = response.json()
        ai_reply = data["choices"][0]["message"]["content"]


    elif req.provider == "openai":


        messages = [
            {"role": "system", "content": SYSTEM_PROMPTS[role]},
            {"role": "user", "content": req.message}
        ]


        response = openai_client.chat.completions.create(
            model=SAFE_CONFIG["model"],
            messages=messages,
            max_completion_tokens=SAFE_CONFIG["max_tokens"]
        )


        msg = response.choices[0].message
        ai_reply = msg.content if isinstance(msg.content, str) else ""


        if not ai_reply.strip():
            ai_reply = "⚠️ OpenAI responded but returned no readable text."

    else:
        return {"error": "Invalid provider"}


    memory.append({
        "role": "assistant",
        "content": ai_reply
    })


    if len(memory) > MAX_MEMORY:
        memory.pop(1)


    response_time = round(time.time() - start_time, 2)
    confidence_score = calculate_confidence(ai_reply, role)
    analytics["total_messages"] += 1

    return {
        "role": role,
        "provider": req.provider,
        "info": f"🔄 Switched to {role.upper()} mode" if role_switched else None,
        "reply": ai_reply,
        "confidence": confidence_score,
        "response_time": response_time
    }

@app.post("/chat-start")
def chat_start():
    analytics["total_chats"] += 1
    return {"status": "chat started"}
#FEEDBACK
@app.post("/feedback")
def feedback(fb: Feedback):
    if fb.value == "up":
        analytics["feedback_up"] += 1
    elif fb.value == "down":
        analytics["feedback_down"] += 1
    return {"status": "recorded"}

@app.get("/analytics")
def get_analytics():
    return analytics


FRONTEND_PATH = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=FRONTEND_PATH, html=True), name="frontend")
