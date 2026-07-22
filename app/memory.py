


from app.database import get_connection


def add_message(session_id, role, content, title=None):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO chat_messages(session_id, role, content, title)
        VALUES (?, ?, ?, ?)
    """, (session_id, role, content, title))

    conn.commit()
    conn.close()


def get_history(session_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT role, content
        FROM chat_messages
        WHERE session_id=?
        ORDER BY id
        """,
        (session_id,)
    )

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "role": row["role"],
            "content": row["content"]
        }
        for row in rows
    ]


def list_sessions():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            session_id,
            MIN(title) AS title,
            MAX(created_at) AS last_activity,
            COUNT(*) AS messages
        FROM chat_messages
        GROUP BY session_id
        ORDER BY last_activity DESC
    """)

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "session_id": row["session_id"],
            "title": row["title"] if row["title"] else row["session_id"],
            "messages": row["messages"],
            "created_at": row["last_activity"]
        }
        for row in rows
    ]


def delete_session(session_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        DELETE FROM chat_messages
        WHERE session_id=?
        """,
        (session_id,)
    )

    conn.commit()
    conn.close()


import json

def get_retrieval_memory(session_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT topic, documents, compared_documents, chapter, page, entity, mode
        FROM session_retrieval_memory
        WHERE session_id = ?
    """, (session_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {
            "topic": None,
            "documents": [],
            "compared_documents": [],
            "chapter": None,
            "page": None,
            "entity": None,
            "mode": None
        }
        
    try:
        docs = json.loads(row["documents"]) if row["documents"] else []
    except Exception:
        docs = []
        
    try:
        comp_docs = json.loads(row["compared_documents"]) if row["compared_documents"] else []
    except Exception:
        comp_docs = []
        
    return {
        "topic": row["topic"],
        "documents": docs,
        "compared_documents": comp_docs,
        "chapter": row["chapter"],
        "page": row["page"],
        "entity": row["entity"],
        "mode": row["mode"]
    }

def save_retrieval_memory(session_id, mem):
    conn = get_connection()
    cursor = conn.cursor()
    docs_json = json.dumps(mem.get("documents", []))
    comp_docs_json = json.dumps(mem.get("compared_documents", []))
    
    cursor.execute("""
        INSERT OR REPLACE INTO session_retrieval_memory(
            session_id, topic, documents, compared_documents, chapter, page, entity, mode, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        session_id,
        mem.get("topic"),
        docs_json,
        comp_docs_json,
        mem.get("chapter"),
        mem.get("page"),
        mem.get("entity"),
        mem.get("mode")
    ))
    conn.commit()
    conn.close()