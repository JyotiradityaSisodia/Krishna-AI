from __future__ import annotations

import json
import os
from typing import Any

DATA_PATH = "D:/krishna/data"
FILE_PATH = os.path.join(DATA_PATH, "task_state.json")


def _default_state() -> dict[str, Any]:
    return {
        "active_tasks": [],
        "current_task_id": None,
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
            if "active_tasks" not in data:
                data["active_tasks"] = []
            if "current_task_id" not in data:
                data["current_task_id"] = None
            return data
    except Exception:
        return _default_state()


def _save(data: dict[str, Any]) -> None:
    _ensure_file()
    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def add_task(task: dict[str, Any]) -> None:
    data = _load()
    data.setdefault("active_tasks", []).append(task)
    data["current_task_id"] = task.get("id")
    _save(data)


def get_active_tasks() -> list[dict[str, Any]]:
    data = _load()
    return data.get("active_tasks", [])


def set_current_task(task_id: str | None) -> None:
    data = _load()
    data["current_task_id"] = task_id
    _save(data)


def get_current_task() -> dict[str, Any] | None:
    data = _load()
    current_id = data.get("current_task_id")
    if not current_id:
        return None

    for task in data.get("active_tasks", []):
        if task.get("id") == current_id:
            return task
    return None


def get_task_by_id(task_id: str) -> dict[str, Any] | None:
    data = _load()
    for task in data.get("active_tasks", []):
        if task.get("id") == task_id:
            return task
    return None


def update_task(task_id: str, updates: dict[str, Any]) -> bool:
    data = _load()
    tasks = data.get("active_tasks", [])

    for idx, task in enumerate(tasks):
        if task.get("id") == task_id:
            task.update(updates)
            tasks[idx] = task
            data["active_tasks"] = tasks
            _save(data)
            return True

    return False


def update_task_step(task_id: str, step_number: int, updates: dict[str, Any]) -> bool:
    data = _load()
    tasks = data.get("active_tasks", [])

    for t_idx, task in enumerate(tasks):
        if task.get("id") != task_id:
            continue

        steps = task.get("steps", [])
        for s_idx, step in enumerate(steps):
            if int(step.get("step", -1)) == int(step_number):
                step.update(updates)
                steps[s_idx] = step
                task["steps"] = steps
                tasks[t_idx] = task
                data["active_tasks"] = tasks
                _save(data)
                return True

    return False


def mark_only_one_step_in_progress(task_id: str, step_number: int) -> bool:
    data = _load()
    tasks = data.get("active_tasks", [])

    for t_idx, task in enumerate(tasks):
        if task.get("id") != task_id:
            continue

        steps = task.get("steps", [])
        found = False

        for s_idx, step in enumerate(steps):
            if int(step.get("step", -1)) == int(step_number):
                step["status"] = "in_progress"
                found = True
            elif step.get("status") == "in_progress":
                step["status"] = "planned"
            steps[s_idx] = step

        if found:
            task["steps"] = steps
            task["status"] = "active"
            tasks[t_idx] = task
            data["active_tasks"] = tasks
            data["current_task_id"] = task_id
            _save(data)
            return True

    return False


def get_next_open_step(task_id: str) -> dict[str, Any] | None:
    task = get_task_by_id(task_id)
    if not task:
        return None

    for step in task.get("steps", []):
        if step.get("status") in {"planned", "in_progress"}:
            return step
    return None


def complete_task(task_id: str) -> bool:
    data = _load()
    tasks = data.get("active_tasks", [])
    changed = False

    for idx, task in enumerate(tasks):
        if task.get("id") == task_id:
            task["status"] = "completed"
            for s_idx, step in enumerate(task.get("steps", [])):
                if step.get("status") != "done":
                    step["status"] = "done"
                task["steps"][s_idx] = step
            tasks[idx] = task
            changed = True
            break

    if changed:
        data["active_tasks"] = tasks
        if data.get("current_task_id") == task_id:
            data["current_task_id"] = None
        _save(data)

    return changed


def pause_task(task_id: str) -> bool:
    return update_task(task_id, {"status": "paused"})


def resume_task(task_id: str) -> bool:
    data = _load()
    tasks = data.get("active_tasks", [])
    found = False

    for idx, task in enumerate(tasks):
        if task.get("id") == task_id:
            task["status"] = "active"
            tasks[idx] = task
            found = True
            break

    if found:
        data["active_tasks"] = tasks
        data["current_task_id"] = task_id
        _save(data)

    return found


def remove_completed_tasks() -> int:
    data = _load()
    tasks = data.get("active_tasks", [])
    kept = [t for t in tasks if t.get("status") != "completed"]
    removed = len(tasks) - len(kept)
    data["active_tasks"] = kept

    current_id = data.get("current_task_id")
    if current_id and not any(t.get("id") == current_id for t in kept):
        data["current_task_id"] = None

    _save(data)
    return removed


def clear_tasks() -> None:
    _save(_default_state())