from __future__ import annotations

from typing import Dict, Any, Optional

from core.schemas import Task
from core.device_router import get_skill, select_target_device
from core.task_store import create_task


def create_unified_task(
    source_device: str,
    skill_name: str,
    intent: str,
    params: Dict[str, Any],
    target_device: Optional[str] = None,
) -> Dict[str, Any]:
    skill = get_skill(skill_name)
    if not skill:
        return {
            "success": False,
            "message": f"Unknown skill: {skill_name}"
        }

    target = target_device or select_target_device(
        skill_name, source_device=source_device)
    if not target:
        return {
            "success": False,
            "message": f"No target device available for skill: {skill_name}"
        }

    task = Task.create(
        source_device=source_device,
        target_device=target,
        skill=skill_name,
        intent=intent,
        params=params,
    )

    stored = create_task(task)

    return {
        "success": True,
        "message": "Unified task created",
        "task": stored
    }
