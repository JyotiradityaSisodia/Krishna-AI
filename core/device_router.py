from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Optional


BASE_DIR = Path(__file__).resolve().parent.parent
REGISTRY_DIR = BASE_DIR / "registry"


def _read_json(filename: str) -> Dict:
    path = REGISTRY_DIR / filename
    return json.loads(path.read_text(encoding="utf-8"))


def load_skills() -> Dict:
    return _read_json("skills.json")


def load_devices() -> Dict:
    return _read_json("devices.json")


def load_capabilities() -> Dict:
    return _read_json("capabilities.json")


def get_skill(skill_name: str) -> Optional[Dict]:
    return load_skills().get(skill_name)


def get_device(device_id: str) -> Optional[Dict]:
    return load_devices().get(device_id)


def get_online_devices() -> Dict:
    return {
        k: v for k, v in load_devices().items()
        if v.get("status") == "online"
    }


def select_target_device(skill_name: str, source_device: Optional[str] = None) -> Optional[str]:
    skills = load_skills()
    devices = get_online_devices()

    skill = skills.get(skill_name)
    if not skill:
        return None

    preferred = skill.get("preferred_device")
    fallback = skill.get("fallback_device")

    if preferred:
        for device_id, info in devices.items():
            if info.get("device_type") == preferred:
                return device_id

    if fallback:
        for device_id, info in devices.items():
            if info.get("device_type") == fallback:
                return device_id

    if source_device and source_device in devices:
        return source_device

    return next(iter(devices.keys()), None)
