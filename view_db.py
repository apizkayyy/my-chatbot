import sqlite3

conn = sqlite3.connect("chat.db")
rows = conn.execute(
    "SELECT id, session_id, role, content FROM messages ORDER BY id"
).fetchall()

for id, session_id, role, content in rows:
    print(f"{id} | {session_id} | {role} | {content[:80]}")

conn.close()