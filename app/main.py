from fastapi import FastAPI
from pydantic import BaseModel

from app.agent import chat, SYSTEM_PROMPT
from app.database import initialize_database, seed_database


app = FastAPI(title="Patient Appointment Agent")


# Store conversations in memory for the demo.
# Each session_id represents one patient's conversation.
conversations = {}


class ChatRequest(BaseModel):
    session_id: str = "default"
    message: str


@app.on_event("startup")
def startup():
    initialize_database()
    seed_database()


@app.get("/")
def health_check():
    return {
        "status": "ok",
        "message": "Patient Appointment Agent is running"
    }


@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    if request.session_id not in conversations:
        conversations[request.session_id] = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

    conversation = conversations[request.session_id]

    response = chat(
        request.message,
        conversation
    )

    return {
        "session_id": request.session_id,
        "response": response
    }


@app.delete("/chat/{session_id}")
def reset_chat(session_id: str):
    conversations.pop(session_id, None)

    return {
        "status": "ok",
        "message": f"Conversation '{session_id}' reset"
    }