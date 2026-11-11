from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

DATA_PATH = "D:/krishna/data"
FILE_PATH = os.path.join(DATA_PATH, "self_improvement.json")


def _default_state() -> dict[str, Any]:
    return {
        "ideas": []
    }


def _ensure_file() -> None:
    os.makedirs(DATA_PATH, exist_ok=True)
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(_default_state(), f, indent=2)


def _load() -> dict[str, Any]:
    _ensure_file()
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            if "ideas" not in data:
                data["ideas"] = []
            return data
    except Exception:
        return _default_state()


def _save(data: dict[str, Any]) -> None:
    _ensure_file()
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def add_idea(title: str, details: str = "", source: str = "manual") -> dict[str, Any]:
    data = _load()
    ideas = data.get("ideas", [])

    idea = {
        "id": f"idea-{int(datetime.now().timestamp())}",
        "title": title.strip(),
        "details": details.strip(),
        "source": source,
        "status": "pending",
        "created_at": datetime.now().isoformat(),
    }

    ideas.append(idea)
    data["ideas"] = ideas
    _save(data)
    return idea


def list_ideas(status: str | None = None) -> list[dict[str, Any]]:
    data = _load()
    ideas = data.get("ideas", [])

    if status is None:
        return ideas

    return [idea for idea in ideas if idea.get("status") == status]


def get_idea_by_id(idea_id: str) -> dict[str, Any] | None:
    data = _load()
    for idea in data.get("ideas", []):
        if idea.get("id") == idea_id:
            return idea
    return None


def get_latest_pending_idea() -> dict[str, Any] | None:
    pending = list_ideas(status="pending")
    if not pending:
        return None
    return pending[-1]


def update_idea_status(idea_id: str, status: str) -> bool:
    data = _load()
    ideas = data.get("ideas", [])

    for idx, idea in enumerate(ideas):
        if idea.get("id") == idea_id:
            idea["status"] = status
            ideas[idx] = idea
            data["ideas"] = ideas
            _save(data)
            return True

    return False


def clear_ideas() -> None:
    _save(_default_state())