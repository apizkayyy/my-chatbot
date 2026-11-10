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

        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS summaries (
                session_id TEXT PRIMARY KEY,
                summary TEXT NOT NULL,
                last_message_id INTEGER NOT NULL
            )
            """
        )


def save_message(session_id: str, role: str, content: str):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content),
        )


def load_history(session_id: str, limit: int | None = None) -> list:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id",
            (session_id,),
        ).fetchall()

    if limit is not None:
        rows = rows[-limit:]

    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    for role, content in rows:
        history.append({"role": role, "content": content})
    return history


def list_sessions() -> list:
    with get_conn() as conn:
        rows = conn.execute("SELECT DISTINCT session_id FROM messages").fetchall()
    return [r[0] for r in rows]

def get_summary(session_id: str) -> tuple[str, int]:
    with get_conn() as conn:
        row = conn.execute(
            "SELECT summary, last_message_id FROM summaries WHERE session_id = ?",
            (session_id,),
        ).fetchone()
    return row if row else ("", 0)


def save_summary(session_id: str, summary: str, last_message_id: int):
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO summaries (session_id, summary, last_message_id) "
            "VALUES (?, ?, ?)",
            (session_id, summary, last_message_id),
        )


def load_unsummarized(session_id: str) -> tuple[str, list]:
    summary, last_id = get_summary(session_id)
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT id, role, content FROM messages "
            "WHERE session_id = ? AND id > ? ORDER BY id",
            (session_id, last_id),
        ).fetchall()
    return summary, rows