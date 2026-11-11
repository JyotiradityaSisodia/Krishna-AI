from __future__ import annotations

import json
import os
from typing import List, Dict

DATA_PATH = "D:/krishna/data"
FILE_PATH = os.path.join(DATA_PATH, "conversations.json")

MAX_HISTORY = 12
MAX_USER_CONTEXT = 6


def _ensure_file():
    os.makedirs(DATA_PATH, exist_ok=True)
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)


def load_history() -> List[Dict[str, str]]:
    _ensure_file()
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_history(history: List[Dict[str, str]]) -> None:
    _ensure_file()
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(history[-MAX_HISTORY:], f, indent=2, ensure_ascii=False)


def add_turn(role: str, content: str) -> None:
    history = load_history()
    history.append({"role": role, "content": content})
    save_history(history)


def get_recent_context() -> str:
    history = load_history()

    if not history:
        return ""

    user_lines = []

    for item in history:
        role = item.get("role", "").strip().lower()
        content = (item.get("content", "") or "").strip()

        if not content:
            continue

        # Only keep user messages in prompt context
        if role == "user":
            user_lines.append(f"User: {content}")

    if not user_lines:
        return ""

    return "\n".join(user_lines[-MAX_USER_CONTEXT:])


def clear_history() -> None:
    save_history([])