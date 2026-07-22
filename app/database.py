import sqlite3
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_NAME = str(PROJECT_ROOT / "documind.db")

try:
    import streamlit as st
    cache_res = st.cache_resource(show_spinner=False)
except Exception:
    def cache_res(fn):
        return fn


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


@cache_res
def initialize_database():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            title TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documents(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT UNIQUE NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    chunks INTEGER DEFAULT 0
)
""")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS session_retrieval_memory (
            session_id TEXT PRIMARY KEY,
            topic TEXT,
            documents TEXT,
            compared_documents TEXT,
            chapter TEXT,
            page INTEGER,
            entity TEXT,
            mode TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def update_chat_title(session_id, title):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE chat_messages
        SET title = ?
        WHERE session_id = ?
    """, (title, session_id))

    conn.commit()
    conn.close()
def add_document(filename, chunks):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO documents(filename, chunks)
        VALUES (?, ?)
    """, (filename, chunks))

    conn.commit()
    conn.close()


def get_documents():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT filename, uploaded_at, chunks
        FROM documents
        ORDER BY uploaded_at DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def delete_document_metadata(filename):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        "DELETE FROM documents WHERE filename=?",
        (filename,)
    )

    conn.commit()
    conn.close()