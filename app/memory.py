import sqlite3
from app.config import DATABASE_PATH


def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        key TEXT NOT NULL,
        value TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS task_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_input TEXT NOT NULL,
        assistant_output TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()


def save_memory(mem_type: str, key: str, value: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO memories (type, key, value) VALUES (?, ?, ?)",
        (mem_type, key, value)
    )
    conn.commit()
    conn.close()


def get_memories(limit: int = 20):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT type, key, value FROM memories ORDER BY id DESC LIMIT ?",
        (limit,)
    )
    rows = cur.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_memory_by_key(search_key: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT type, key, value FROM memories WHERE LOWER(key) = LOWER(?) ORDER BY id DESC LIMIT 1",
        (search_key,)
    )
    row = cur.fetchone()
    conn.close()
    return dict(row) if row else None


def log_task(user_input: str, assistant_output: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO task_logs (user_input, assistant_output) VALUES (?, ?)",
        (user_input, assistant_output)
    )
    conn.commit()
    conn.close()