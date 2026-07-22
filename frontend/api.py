import os
import requests

BASE_URL = os.getenv("BACKEND_API_URL", "http://127.0.0.1:8000")


def upload_documents(files):
    file_data = []

    for file in files:
        file_data.append(
            (
                "files",
                (file.name, file.getvalue(), "application/pdf")
            )
        )

    response = requests.post(
        f"{BASE_URL}/upload",
        files=file_data
    )

    return response.json()


def get_documents():
    response = requests.get(
        f"{BASE_URL}/documents"
    )

    return response.json()


def ask_question(session_id, question, document=None):

    payload = {
        "session_id": session_id,
        "question": question,
        "document": document
    }

    response = requests.post(
        f"{BASE_URL}/ask",
        json=payload
    )

    return response.json()


def get_chats():
    return requests.get(
        f"{BASE_URL}/chats"
    ).json()


def get_chat(session_id):
    return requests.get(
        f"{BASE_URL}/chat/{session_id}"
    ).json()


def delete_chat(session_id):
    return requests.delete(
        f"{BASE_URL}/chat/{session_id}"
    ).json()