from __future__ import annotations

import json
import os
from typing import List, Dict

DATA_PATH = "D:/krishna/data"
FILE_PATH = os.path.join(DATA_PATH, "long_term_memory.json")


def _ensure_file():
    os.makedirs(DATA_PATH, exist_ok=True)
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, "w") as f:
            json.dump([], f)


def load_all() -> List[Dict[str, str]]:
    _ensure_file()
    try:
        with open(FILE_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return []


def save_all(data: List[Dict[str, str]]) -> None:
    _ensure_file()
    with open(FILE_PATH, "w") as f:
        json.dump(data, f, indent=2)


def store_conversation(user: str, assistant: str) -> None:
    data = load_all()

    data.append({
        "user": user,
        "assistant": assistant
    })

    save_all(data)


def search_memory(query: str, limit: int = 5) -> str:
    data = load_all()
    query = query.lower()

    scored = []

    for item in data:
        text = f"{item['user']} {item['assistant']}".lower()

        score = 0
        for word in query.split():
            if word in text:
                score += 1

        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for _, item in scored[:limit]:
        results.append(f"User: {item['user']}\nAssistant: {item['assistant']}")

    return "\n".join(results)