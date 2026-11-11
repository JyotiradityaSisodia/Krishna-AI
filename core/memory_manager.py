from __future__ import annotations
from typing import Any, Dict
from pathlib import Path
import json
from app.memory import get_memory_by_key, log_task


def handle_memory_lookup(user_input: str):
    text = user_input.lower().strip()

    if "what food do i like" in text or "what is my favorite food" in text:
        memory = get_memory_by_key(
            "food") or get_memory_by_key("favorite_food")
        if memory:
            reply = f"You told me your food preference is {memory['value']}."
            log_task(user_input, reply)
            return reply

    return None


BASE_DIR = Path(__file__).resolve().parent.parent
MEMORY_DIR = BASE_DIR / "memory"
PROFILE_FILE = MEMORY_DIR / "user_profile.json"


DEFAULT_PROFILE = {
    "assistant_identity": {
        "name": "Krishna",
        "voice_id": "krishna_primary",
        "personality": "calm_confident_helpful"
    },
    "user_preferences": {
        "preferred_food_platform": "zomato",
        "preferred_device_for_food": "android",
        "preferred_device_for_code": "desktop"
    },
    "shared_context": {
        "last_active_device": "desktop-main"
    }
}


def _ensure() -> None:
    MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    if not PROFILE_FILE.exists():
        PROFILE_FILE.write_text(json.dumps(
            DEFAULT_PROFILE, indent=2), encoding="utf-8")


def load_profile() -> Dict[str, Any]:
    _ensure()
    return json.loads(PROFILE_FILE.read_text(encoding="utf-8"))


def save_profile(profile: Dict[str, Any]) -> None:
    _ensure()
    PROFILE_FILE.write_text(json.dumps(profile, indent=2), encoding="utf-8")


def update_profile(path: list[str], value: Any) -> Dict[str, Any]:
    profile = load_profile()
    current = profile
    for key in path[:-1]:
        current = current.setdefault(key, {})
    current[path[-1]] = value
    save_profile(profile)
    return profile
