import sqlite3
from config import SYSTEM_PROMPT

DB_FILE = "chat.db"


def get_conn():
    return sqlite3.connect(DB_FILE)


def init_db():
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL
            )
            """
        )


def save_message(session_id: str, role: str, content: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content),
        )


def load_history(session_id: str) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()

    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    for role, content in rows:
        history.append({"role": role, "content": content})
    return history


def list_sessions() -> list:
    with get_conn() as conn:
        rows = conn.execute("SELECT DISTINCT session_id FROM messages").fetchall()
    return [r[0] for r in rows]