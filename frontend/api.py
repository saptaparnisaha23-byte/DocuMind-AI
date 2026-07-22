import os
import requests
from pathlib import Path

import streamlit as st

BASE_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")

@st.cache_resource(show_spinner=False)
def check_standalone_cached():
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=0.5)
        return r.status_code != 200
    except Exception:
        return True

# Standalone Standby Mode indicator
STANDALONE_MODE = check_standalone_cached()

def upload_documents(files):
    if STANDALONE_MODE:
        import shutil
        from app.ingest import ingest_pdf
        UPLOAD_FOLDER = Path("uploads")
        UPLOAD_FOLDER.mkdir(exist_ok=True)
        uploaded = []
        for file in files:
            save_path = UPLOAD_FOLDER / file.name
            with open(save_path, "wb") as buffer:
                buffer.write(file.getbuffer() if hasattr(file, "getbuffer") else file.read())
            result = ingest_pdf(save_path)
            uploaded.append(result)
        return {
            "success": True,
            "message": f"{len(uploaded)} document(s) uploaded successfully.",
            "documents": uploaded
        }

    file_data = []
    for file in files:
        file_data.append(
            (
                "files",
                (file.name, file.getvalue(), "application/pdf")
            )
        )
    try:
        response = requests.post(
            f"{BASE_URL}/upload",
            files=file_data
        )
        return response.json()
    except Exception as e:
        return {"success": False, "detail": f"Connection error: {e}"}

def get_documents():
    if STANDALONE_MODE:
        UPLOAD_FOLDER = Path("uploads")
        UPLOAD_FOLDER.mkdir(exist_ok=True)
        pdf_files = list(UPLOAD_FOLDER.glob("*.pdf"))
        pdf_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        documents = [file.name for file in pdf_files]
        return {
            "success": True,
            "count": len(documents),
            "documents": documents
        }

    try:
        response = requests.get(
            f"{BASE_URL}/documents"
        )
        return response.json()
    except Exception:
        return {"success": True, "count": 0, "documents": []}

def ask_question(session_id, question, document=None):
    if STANDALONE_MODE:
        from app.chatbot import ask_question as run_ask
        res = run_ask(session_id, question, document)
        return {
            "success": res["success"],
            "data": {
                "answer": res["answer"],
                "sources": res["sources"],
                "confidence": res["confidence"]
            }
        }

    payload = {
        "session_id": session_id,
        "question": question,
        "document": document
    }
    try:
        response = requests.post(
            f"{BASE_URL}/ask",
            json=payload
        )
        return response.json()
    except Exception as e:
        return {"success": False, "detail": f"Connection error: {e}"}

def get_chats():
    if STANDALONE_MODE:
        from app.memory import list_sessions
        return {
            "success": True,
            "chats": list_sessions()
        }

    try:
        return requests.get(
            f"{BASE_URL}/chats"
        ).json()
    except Exception:
        return {"success": True, "chats": []}

def get_chat(session_id):
    if STANDALONE_MODE:
        from app.memory import get_history
        return {
            "success": True,
            "messages": get_history(session_id)
        }

    try:
        return requests.get(
            f"{BASE_URL}/chat/{session_id}"
        ).json()
    except Exception:
        return {"success": True, "messages": []}

def delete_chat(session_id):
    if STANDALONE_MODE:
        from app.memory import delete_session
        delete_session(session_id)
        return {
            "success": True,
            "message": "Chat deleted successfully."
        }

    try:
        return requests.delete(
            f"{BASE_URL}/chat/{session_id}"
        ).json()
    except Exception as e:
        return {"success": False, "detail": str(e)}

def delete_document_api(filename):
    if STANDALONE_MODE:
        try:
            UPLOAD_FOLDER = Path("uploads")
            file_path = UPLOAD_FOLDER / filename
            if file_path.exists():
                file_path.unlink()
            from app.embed import delete_document as delete_embeddings
            delete_embeddings(filename)
            from app.database import delete_document_metadata
            delete_document_metadata(filename)
            return {"success": True, "message": f"{filename} deleted successfully."}
        except Exception as e:
            return {"success": False, "detail": str(e)}
    else:
        try:
            return requests.delete(
                f"{BASE_URL}/documents/{filename}"
            ).json()
        except Exception as e:
            return {"success": False, "detail": f"Connection error: {e}"}