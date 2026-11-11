from __future__ import annotations

import json
import os
from datetime import datetime
from typing import Any

JOURNAL_FILE = os.path.join("data", "journal.json")


def _ensure_parent() -> None:
    os.makedirs(os.path.dirname(JOURNAL_FILE), exist_ok=True)


def _load() -> list[dict[str, Any]]:
    _ensure_parent()

    if not os.path.exists(JOURNAL_FILE):
        return []

    try:
        with open(JOURNAL_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            return []
    except Exception:
        return []


def _save(data: list[dict[str, Any]]) -> None:
    _ensure_parent()
    with open(JOURNAL_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def log_entry(
    category: str,
    task: str,
    result: str,
    reason: str = "",
    notes: str = "",
    priority: str = "normal",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    data = _load()

    entry = {
        "time": datetime.utcnow().isoformat(),
        "category": category,
        "task": task,
        "result": result,
        "reason": reason,
        "notes": notes,
        "priority": priority,
        "metadata": metadata or {},
    }

    data.append(entry)
    _save(data)
    return entry


def get_recent(n: int = 10) -> list[dict[str, Any]]:
    data = _load()
    if n <= 0:
        return []
    return data[-n:]


def get_all() -> list[dict[str, Any]]:
    return _load()


def count_results() -> dict[str, int]:
    data = _load()
    counts: dict[str, int] = {}

    for entry in data:
        result = str(entry.get("result", "unknown")).lower()
        counts[result] = counts.get(result, 0) + 1

    return counts


def find_by_category(category: str, limit: int = 20) -> list[dict[str, Any]]:
    category = category.strip().lower()
    data = _load()

    matches = [
        entry for entry in data
        if str(entry.get("category", "")).lower() == category
    ]

    return matches[-limit:]


def find_by_task_contains(text: str, limit: int = 20) -> list[dict[str, Any]]:
    needle = text.strip().lower()
    if not needle:
        return []

    data = _load()
    matches = [
        entry for entry in data
        if needle in str(entry.get("task", "")).lower()
    ]
    return matches[-limit:]


def get_failure_entries(limit: int = 20) -> list[dict[str, Any]]:
    data = _load()
    failures = [
        entry for entry in data
        if str(entry.get("result", "")).lower() == "failed"
    ]
    return failures[-limit:]


def summarize_recent(limit: int = 12) -> dict[str, Any]:
    recent = get_recent(limit)
    result_counts: dict[str, int] = {}
    category_counts: dict[str, int] = {}

    for entry in recent:
        result = str(entry.get("result", "unknown")).lower()
        category = str(entry.get("category", "uncategorized")).lower()

        result_counts[result] = result_counts.get(result, 0) + 1
        category_counts[category] = category_counts.get(category, 0) + 1

    return {
        "total_entries_considered": len(recent),
        "result_counts": result_counts,
        "category_counts": category_counts,
        "recent": recent,
    }