from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

MEMORY_FILE = os.path.join("data", "memory.json")


def _ensure_parent() -> None:
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)


def _default_memory() -> dict[str, Any]:
    return {
        "facts": [],
        "preferences": [],
        "notes": [],
        "updated_at": None,
    }


def _load() -> dict[str, Any]:
    _ensure_parent()

    if not os.path.exists(MEMORY_FILE):
        data = _default_memory()
        _save(data)
        return data

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                for key in ["facts", "preferences", "notes"]:
                    data.setdefault(key, [])
                data.setdefault("updated_at", None)
                return data
    except Exception:
        pass

    data = _default_memory()
    _save(data)
    return data


def _save(data: dict[str, Any]) -> None:
    _ensure_parent()
    data["updated_at"] = datetime.utcnow().isoformat()
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_memory() -> dict[str, Any]:
    return _load()


def add_memory(category: str, text: str) -> dict[str, Any]:
    category = category.strip().lower()
    text = text.strip()

    if category not in {"facts", "preferences", "notes"}:
        raise ValueError("Invalid memory category.")

    if not text:
        raise ValueError("Memory text cannot be empty.")

    data = _load()

    if text not in data[category]:
        data[category].append(text)
        _save(data)

    return {
        "success": True,
        "category": category,
        "stored": text,
        "message": f"Stored in Krishna memory under {category}.",
    }


def remove_memory(text: str) -> dict[str, Any]:
    target = text.strip().lower()

    if not target:
        return {
            "success": False,
            "message": "Tell me what memory to remove.",
        }

    data = _load()
    removed = []

    for category in ["facts", "preferences", "notes"]:
        kept = []
        for item in data[category]:
            if target in item.lower():
                removed.append({"category": category, "text": item})
            else:
                kept.append(item)
        data[category] = kept

    if removed:
        _save(data)
        return {
            "success": True,
            "removed": removed,
            "message": f"Removed {len(removed)} memory item(s).",
        }

    return {
        "success": False,
        "removed": [],
        "message": "No matching memory found.",
    }


def summarize_memory() -> dict[str, Any]:
    data = _load()
    return {
        "facts": data["facts"],
        "preferences": data["preferences"],
        "notes": data["notes"],
        "updated_at": data["updated_at"],
    }


def build_memory_context(limit_per_category: int = 5) -> str:
    data = _load()

    facts = data["facts"][-limit_per_category:]
    preferences = data["preferences"][-limit_per_category:]
    notes = data["notes"][-limit_per_category:]

    lines: list[str] = []

    if facts:
        lines.append("User facts:")
        lines.extend([f"- {x}" for x in facts])

    if preferences:
        lines.append("User preferences:")
        lines.extend([f"- {x}" for x in preferences])

    if notes:
        lines.append("Important notes:")
        lines.extend([f"- {x}" for x in notes])

    return "\n".join(lines).strip()