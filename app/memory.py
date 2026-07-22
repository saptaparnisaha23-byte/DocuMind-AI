


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