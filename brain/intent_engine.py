from __future__ import annotations

from typing import Any


def normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def classify_intent(user_input: str) -> dict[str, Any]:
    text = normalize(user_input)

    if not text:
        return {
            "intent": "empty",
            "confidence": 1.0,
            "entities": {},
        }

    # -------------------------
    # Memory intents
    # -------------------------
    if text.startswith("remember that "):
        return {
            "intent": "memory_add_fact",
            "confidence": 0.99,
            "entities": {
                "content": user_input[len("remember that "):].strip()
            },
        }

    if text.startswith("remember this preference:"):
        return {
            "intent": "memory_add_preference",
            "confidence": 0.99,
            "entities": {
                "content": user_input[len("remember this preference:"):].strip()
            },
        }

    if text.startswith("remember this note:"):
        return {
            "intent": "memory_add_note",
            "confidence": 0.99,
            "entities": {
                "content": user_input[len("remember this note:"):].strip()
            },
        }

    if text in {"what do you remember", "show memory", "memory status"}:
        return {
            "intent": "memory_show",
            "confidence": 0.99,
            "entities": {},
        }

    if text.startswith("forget "):
        return {
            "intent": "memory_forget",
            "confidence": 0.99,
            "entities": {
                "content": user_input[len("forget "):].strip()
            },
        }

    # -------------------------
    # Auto-learning hints
    # -------------------------
    if "i like" in text or "i prefer" in text:
        return {
            "intent": "auto_preference_capture",
            "confidence": 0.85,
            "entities": {
                "content": user_input.strip()
            },
        }

    if "my name is" in text or text.startswith("i am "):
        return {
            "intent": "auto_fact_capture",
            "confidence": 0.85,
            "entities": {
                "content": user_input.strip()
            },
        }

    # -------------------------
    # Upgrade intents
    # -------------------------
    if text.startswith("learn "):
        return {
            "intent": "upgrade_request",
            "confidence": 0.99,
            "entities": {
                "ability": user_input[len("learn "):].strip()
            },
        }

    if text.startswith("krishna learn "):
        return {
            "intent": "upgrade_request",
            "confidence": 0.99,
            "entities": {
                "ability": user_input[len("krishna learn "):].strip()
            },
        }

    if text.startswith("approve "):
        return {
            "intent": "upgrade_approve",
            "confidence": 0.99,
            "entities": {
                "ability": user_input[len("approve "):].strip()
            },
        }

    # -------------------------
    # Advisor intent
    # -------------------------
    if (
        "what should we do next" in text
        or "what should you do next" in text
        or "what should you improve" in text
        or "next step" in text
    ):
        return {
            "intent": "advisor_next_step",
            "confidence": 0.95,
            "entities": {},
        }

    # -------------------------
    # Simple emotional / need intents
    # -------------------------
    if "i'm hungry" in text or "i am hungry" in text:
        return {
            "intent": "user_need_food",
            "confidence": 0.90,
            "entities": {},
        }

    if "i'm tired" in text or "i am tired" in text:
        return {
            "intent": "user_need_rest",
            "confidence": 0.90,
            "entities": {},
        }

    if "i'm bored" in text or "i am bored" in text:
        return {
            "intent": "user_need_activity",
            "confidence": 0.90,
            "entities": {},
        }

    # -------------------------
    # General chat fallback
    # -------------------------
    return {
        "intent": "general_chat",
        "confidence": 0.60,
        "entities": {},
    }


def build_intent_hint(intent_result: dict[str, Any]) -> str:
    intent = intent_result.get("intent", "general_chat")
    confidence = intent_result.get("confidence", 0.0)

    return f"Detected intent: {intent} (confidence {confidence:.2f})"