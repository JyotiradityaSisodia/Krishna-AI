from __future__ import annotations

from core.fallback_knowledge import lookup_knowledge, generic_explanatory_reply


def is_general_question(user_text: str) -> bool:
    text = (user_text or "").strip().lower()

    general_starts = [
        "what is",
        "what are",
        "whats",
        "tell me about",
        "explain",
        "who is",
        "define",
        "how does",
        "why does",
    ]

    if any(text.startswith(prefix) for prefix in general_starts):
        return True

    action_keywords = [
        "open ",
        "tap ",
        "click ",
        "order ",
        "call ",
        "message ",
        "search ",
        "launch ",
    ]

    if any(text.startswith(prefix) for prefix in action_keywords):
        return False

    return True


def provider_free_chat_reply(prompt: str) -> str:
    print("\n=== CHAT ENGINE CALLED ===\n")

    try:
        prompt_text = (prompt or "").strip()
        lower_prompt = prompt_text.lower()

        # Extract the most relevant current question from the prompt
        current_question = ""

        markers = [
            "current question (focus only on this):",
            "user request:",
            "user:",
        ]

        for marker in markers:
            if marker in lower_prompt:
                start = lower_prompt.rfind(marker)
                extracted = prompt_text[start + len(marker):].strip()
                if "\n" in extracted:
                    extracted = extracted.split("\n", 1)[0].strip()
                current_question = extracted
                break

        if not current_question:
            current_question = prompt_text

        # First try explicit knowledge lookup
        result = lookup_knowledge(current_question)

        # Then fall back to generic explanation if needed
        if not result:
            if is_general_question(current_question):
                result = generic_explanatory_reply(current_question)
            else:
                result = "I am ready, sir."

        result = str(result).strip()

        print("\n=== CHAT ENGINE RAW OUTPUT ===\n")
        print(result)

        return result

    except Exception as e:
        print("CHAT ENGINE ERROR:", e)
        return ""