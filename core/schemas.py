from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import uuid


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id() -> str:
    return str(uuid.uuid4())


@dataclass
class DeviceInfo:
    device_id: str
    device_name: str
    device_type: str
    status: str = "online"
    capabilities: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class SkillDefinition:
    skill: str
    description: str
    required_params: List[str]
    optional_params: List[str] = field(default_factory=list)
    preferred_device: Optional[str] = None
    fallback_device: Optional[str] = None
    response_mode: str = "task_status"
    supports_cross_device: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TaskResult:
    success: bool
    message: str
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Task:
    task_id: str
    created_at: str
    source_device: str
    target_device: str
    skill: str
    intent: str
    params: Dict[str, Any]
    status: str = "queued"
    priority: str = "normal"
    requires_confirmation: bool = False
    result: Optional[TaskResult] = None
    error: Optional[str] = None

    @classmethod
    def create(
        cls,
        source_device: str,
        target_device: str,
        skill: str,
        intent: str,
        params: Dict[str, Any],
        priority: str = "normal",
        requires_confirmation: bool = False,
    ) -> "Task":
        return cls(
            task_id=new_id(),
            created_at=utc_now_iso(),
            source_device=source_device,
            target_device=target_device,
            skill=skill,
            intent=intent,
            params=params,
            status="queued",
            priority=priority,
            requires_confirmation=requires_confirmation,
        )

    def to_dict(self) -> Dict[str, Any]:
        payload = asdict(self)
        if self.result is not None:
            payload["result"] = self.result.to_dict()
        return payload


ALLOWED_TASK_STATUSES = {
    "queued",
    "dispatched",
    "running",
    "waiting_user",
    "completed",
    "failed",
    "cancelled",
}