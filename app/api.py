import time
from datetime import datetime

from fastapi import FastAPI
from pydantic import BaseModel

from app.database import initialize_database

from app.chatbot import ask_question
from app.document_routes import router as document_router
from app.memory import (
    list_sessions,
    get_history,
    delete_session
)
app = FastAPI(
    title="DocuMind-AI API",
    description="AI-powered document question answering system",
    version="1.0.0"
)


initialize_database()
app.openai_version="3.0.3"

# Register Document Routes
app.include_router(document_router)


class QuestionRequest(BaseModel):
    session_id: str
    question: str
    document: str | None = None


@app.get("/")
def home():
    return {
        "success": True,
        "message": "Welcome to DocuMind-AI API 🚀",
        "version": "1.0.0"
    }


@app.get("/health")
def health():
    return {
        "success": True,
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/chats")
def get_all_chats():

    return {
        "success": True,
        "count": len(list_sessions()),
        "chats": list_sessions()
    }

@app.delete("/chat/{session_id}")
def delete_chat(session_id: str):

    delete_session(session_id)

    return {
        "success": True,
        "message": "Chat deleted successfully."
    }
@app.get("/chat/{session_id}")
def load_chat(session_id: str):

    history = get_history(session_id)

    return {
        "success": True,
        "messages": history
    }
@app.post("/ask")
def ask(data: QuestionRequest):

    start_time = time.time()

    result = ask_question(
        session_id=data.session_id,
        question=data.question,
        document=data.document
    )

    execution_time = round(time.time() - start_time, 3)

    return {
        "success": result["success"],
        "message": (
            "Answer generated successfully"
            if result["success"]
            else "Request could not be completed"
        ),
        "data": {
            "answer": result["answer"],
            "sources": result["sources"],
            "confidence": result["confidence"]
        },
        "response_time": f"{execution_time} sec",
        "timestamp": datetime.now().isoformat()
    }