from __future__ import annotations

from typing import Any

from brain.memory_store import get_memory


def normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def quick_reply(user_input: str) -> str | None:
    text = normalize(user_input)

    if text in {"hey krishna", "hi krishna", "krishna", "hey", "hi"}:
        return "Yes, sir."

    if text in {"how are you", "how are you doing"}:
        return "Fully operational, sir."

    if text in {"what are you doing", "what are you up to"}:
        return "Standing by, sir."

    if text == "what should we do next":
        return "We should strengthen Krishna's reliability and reasoning next, sir."

    if text == "stop listening":
        return "Understood, sir. Entering sleep mode."

    if text in {"thanks", "thank you"}:
        return "Always, sir."

    return None


def smart_decision(user_input: str, intent: str) -> dict[str, Any]:
    text = normalize(user_input)
    memory = get_memory()

    if intent == "advisor_next_step":
        return {
            "action": "direct_reply",
            "reply": "My recommendation, sir, is to improve Krishna's reliability, then build the task engine.",
        }

    if intent == "user_need_food":
        return {
            "action": "direct_reply",
            "reply": "You sound hungry, sir. Eat first, then we continue.",
        }

    if intent == "user_need_rest":
        return {
            "action": "direct_reply",
            "reply": "You sound tired, sir. A short break would help.",
        }

    if intent == "user_need_activity":
        return {
            "action": "direct_reply",
            "reply": "You sound bored, sir. We can improve Krishna or do something useful now.",
        }

    notes = " ".join(memory.get("notes", [])).lower()
    if "self learning" in notes or "self upgrading" in notes:
        if "next" in text or "what should" in text:
            return {
                "action": "direct_reply",
                "reply": "Since self-learning and self-upgrading are central, I recommend building orchestration and the task engine next, sir.",
            }

    return {
        "action": "model_fallback",
        "reply": None,
    }


def proactive_suggestion(user_input: str) -> str | None:
    text = normalize(user_input)
    memory = get_memory()

    preferences = " ".join(memory.get("preferences", [])).lower()
    notes = " ".join(memory.get("notes", [])).lower()

    if "self learning" in notes or "self upgrading" in notes:
        if "works" in text or "done" in text or "finished" in text:
            return "Proactive suggestion: strengthen reasoning and task execution next, sir."

    if "short replies" in preferences:
        if "next" in text:
            return "Proactive suggestion: reliability first, then autonomy, sir."

    return None