from __future__ import annotations

from typing import Optional

from brain.identity import SYSTEM_IDENTITY_RULES


BAD_INPUTS = {
    "",
    "ok",
    "okay",
    "hmm",
    "uh",
    "um",
}

WAKE_INPUTS = {
    "hey",
    "hi",
    "krishna",
    "hey krishna",
    "hi krishna",
    "hare krishna",
}


def normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def is_bad_input(text: str) -> bool:
    t = normalize(text)
    return not t or t in BAD_INPUTS


def safe_wake_reply(text: str) -> Optional[str]:
    t = normalize(text)

    if t in WAKE_INPUTS:
        return "Yes, sir."

    if t == "stop listening":
        return "Understood. Entering sleep mode."

    return None


def reply_looks_bad(reply: str) -> bool:
    r = normalize(reply)

    if not r:
        return True

    if len(r) < 5:
        return True

    forbidden_patterns = [
        "system prompt",
        "assistant reply:",
        "current question",
        "recent context",
        "user memory",
        "gemini api",
        "google ai",
        "ollama",
        "language model",
        "llm",
        "trained by",
        "internal architecture",
    ]

    return any(pattern in r for pattern in forbidden_patterns)


def should_offer_deeper_breakdown(user_input: str, reply: str) -> bool:
    user = normalize(user_input)
    text = (reply or "").strip()

    if not text:
        return False

    deep_keywords = [
        "deep",
        "deeply",
        "research",
        "thorough",
        "complete guide",
        "everything about",
        "full explanation",
        "advanced explanation",
    ]

    medium_keywords = [
        "explain",
        "in detail",
        "detailed",
        "describe",
        "break down",
        "walk me through",
    ]

    if any(k in user for k in deep_keywords):
        return False

    if any(k in user for k in medium_keywords):
        return len(text) < 1200

    explanation_starts = [
        "what is",
        "what are",
        "explain",
        "tell me about",
        "how does",
        "why does",
        "why is",
        "who is",
    ]

    if any(user.startswith(prefix) for prefix in explanation_starts):
        return len(text) < 700

    return False


def sanitize_reply(reply: str, user_input: str) -> str:
    cleaned = (reply or "").strip()
    user = normalize(user_input)
    reply_lower = normalize(cleaned)

    # Identity questions
    if any(q in user for q in ["who are you", "introduce yourself", "what are you"]):
        return "I am Krishna, your personal AI assistant."

    if "what model are you" in user or "which model are you" in user:
        return "I am Krishna. I do not expose my internal systems."

    # Wake handling
    wake = safe_wake_reply(user_input)
    if wake and user in WAKE_INPUTS:
        return wake

    # Only block explicit model/provider self-references, not normal factual mentions
    blocked_phrases = [
        "i am gemini",
        "i am google",
        "i am gpt",
        "i am openai",
        "i am ollama",
        "as an ai language model",
        "as a language model",
        "i was trained by",
        "i am an ai model",
        "i am a large language model",
        "system prompt",
        "internal architecture",
        "backend provider",
    ]

    if any(phrase in reply_lower for phrase in blocked_phrases):
        return "I am Krishna."

    # Empty / broken replies
    if not cleaned:
        return "I did not catch that clearly."

    if reply_looks_bad(cleaned):
        return "Understood."

    # Cleanup
    cleaned = cleaned.replace("\r", "").strip()
    cleaned = cleaned.replace(", sir, sir", ", sir")
    cleaned = cleaned.replace("sir, sir", "sir")

    return cleaned


def jarvisify_reply(user_input: str, reply: str) -> str:
    user = normalize(user_input)
    text = (reply or "").strip()

    if not text:
        return "Yes, sir."

    if user in WAKE_INPUTS:
        return "Yes, sir."

    if user == "stop listening":
        return "Understood. Entering sleep mode."

    replacements = {
        "i can help with that": "Of course",
        "certainly": "Of course",
        "i'm sorry": "Apologies",
    }

    lowered = text.lower()
    for old, new in replacements.items():
        if lowered.startswith(old):
            text = new + text[len(old):]
            break

    text = text.strip(" -:\n\t")
    text = text.replace(", sir, sir", ", sir")
    text = text.replace("sir, sir", "sir")
    text = text.replace("sir, is", "is")
    text = text.replace("sir, are", "are")
    text = text.replace("sir, was", "was")
    text = text.replace("sir, uses", "uses")
    text = text.replace("sir, utilizes", "utilizes")
    text = text.replace("sir, represents", "represents")

    if not text:
        return "Understood."

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return "Understood."

    rebuilt = "\n".join(lines)
    low = rebuilt.lower()

    if "sir" not in low and len(rebuilt) < 120:
        if rebuilt.endswith("."):
            rebuilt = rebuilt[:-1] + ", sir."
        elif rebuilt.endswith(("?", "!")):
            rebuilt += " sir."
        else:
            rebuilt += ", sir."

    help_triggers = [
    "explain",
    "teach",
    "what is",
    "what are",
    "how does",
    "help me",
    "guide me",
    "my backend",
    "debug",
]

    if any(trigger in user for trigger in help_triggers):
        polite_openers = [
            "Certainly, sir.",
            "Of course, sir.",
            "Understood, sir.",
        ]

        lower_rebuilt = rebuilt.lower()
        if not (
            lower_rebuilt.startswith("certainly, sir")
            or lower_rebuilt.startswith("of course, sir")
            or lower_rebuilt.startswith("understood, sir")
        ):
            rebuilt = f"{polite_openers[0]} {rebuilt}"
    
    if should_offer_deeper_breakdown(user_input, rebuilt):
        if not rebuilt.endswith(("?", ".", "!")):
            rebuilt += "."
        rebuilt += " Would you like a deeper breakdown?"

    return rebuilt


def build_safe_prompt(
    user_input: str,
    memory_context: str = "",
    conversation_context: str = "",
    long_memory: str = "",
    web_context: str = "",
) -> str:
    parts = []

    parts.append(SYSTEM_IDENTITY_RULES)

    if conversation_context:
        parts.append(f"Recent context:\n{conversation_context}")

    if long_memory:
        parts.append(f"Relevant past context:\n{long_memory}")

    if memory_context:
        parts.append(f"User memory:\n{memory_context}")

    if web_context:
        parts.append(f"Web data:\n{web_context[:1200]}")

    parts.append(f"User: {user_input}")
    parts.append("Reply naturally, intelligently, and completely.")

    return "\n\n".join(parts)