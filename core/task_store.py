from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from core.schemas import Task, TaskResult


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
TASKS_FILE = DATA_DIR / "tasks.json"


def _ensure_storage() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not TASKS_FILE.exists():
        TASKS_FILE.write_text("[]", encoding="utf-8")


def _load_raw() -> List[Dict]:
    _ensure_storage()
    return json.loads(TASKS_FILE.read_text(encoding="utf-8"))


def _save_raw(items: List[Dict]) -> None:
    _ensure_storage()
    TASKS_FILE.write_text(json.dumps(items, indent=2), encoding="utf-8")


def create_task(task: Task) -> Dict:
    items = _load_raw()
    items.append(task.to_dict())
    _save_raw(items)
    return task.to_dict()


def list_tasks() -> List[Dict]:
    return _load_raw()


def get_task(task_id: str) -> Optional[Dict]:
    for item in _load_raw():
        if item["task_id"] == task_id:
            return item
    return None


def update_task_status(task_id: str, status: str) -> Optional[Dict]:
    items = _load_raw()
    updated = None

    for item in items:
        if item["task_id"] == task_id:
            item["status"] = status
            updated = item
            break

    _save_raw(items)
    return updated


def complete_task(task_id: str, success: bool, message: str, data: Optional[Dict] = None) -> Optional[Dict]:
    items = _load_raw()
    updated = None

    for item in items:
        if item["task_id"] == task_id:
            item["status"] = "completed" if success else "failed"
            item["result"] = TaskResult(
                success=success,
                message=message,
                data=data or {}
            ).to_dict()
            updated = item
            break

    _save_raw(items)
    return updated


def tasks_for_target_device(device_id: str, statuses: Optional[List[str]] = None) -> List[Dict]:
    statuses = statuses or ["queued", "dispatched", "running", "waiting_user"]
    return [
        item for item in _load_raw()
        if item["target_device"] == device_id and item["status"] in statuses
    ]
