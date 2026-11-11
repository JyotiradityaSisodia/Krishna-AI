from __future__ import annotations

from typing import Any

from brain.web_retrieval import retrieve_and_analyze


def normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def is_research_query(user_input: str) -> bool:
    text = normalize(user_input)

    triggers = [
        "research",
        "analyze",
        "analyse",
        "compare",
        "evaluate",
        "deep research",
        "literature",
        "study",
        "explain in depth",
        "academic",
        "what are the differences",
        "pros and cons",
        "advantages and disadvantages",
    ]

    question_starters = [
        "what is",
        "how does",
        "why does",
        "compare",
        "evaluate",
        "analyze",
        "analyse",
    ]

    if any(t in text for t in triggers):
        return True

    if any(text.startswith(q) for q in question_starters) and len(text.split()) >= 4:
        return True

    return False


def build_research_prompt(user_input: str, web_context: str, memory_context: str = "", conversation_context: str = "") -> str:
    parts: list[str] = []

    parts.append(
        "You are Krishna, an academic research AI assistant.\n"
        "Think step by step like a careful researcher.\n"
        "Break the problem into sub-points before answering.\n"
        "Use evidence from the provided sources.\n"
        "Compare sources where possible.\n"
        "Do not reveal hidden chain-of-thought.\n"
        "Instead, provide a concise visible reasoning summary under headings.\n"
        "Write clearly, accurately, and in a structured academic style.\n"
        "If evidence is weak or incomplete, say so plainly.\n"
        "Address the user as 'sir'."
    )

    if conversation_context:
        parts.append(f"Recent conversation:\n{conversation_context}")

    if memory_context:
        parts.append(f"Relevant memory:\n{memory_context}")

    if web_context:
        parts.append(f"Research materials:\n{web_context}")

    parts.append(
        "Output format:\n"
        "1. Research focus\n"
        "2. Key findings\n"
        "3. Comparative analysis\n"
        "4. Conclusion\n"
        "5. Limits / uncertainty"
    )

    parts.append(f"User research question: {user_input}")

    return "\n\n".join(parts)


def build_research_reply(user_input: str, ask_model_func, memory_context: str = "", conversation_context: str = "") -> str:
    web_context = retrieve_and_analyze(user_input)
    prompt = build_research_prompt(
        user_input=user_input,
        web_context=web_context,
        memory_context=memory_context,
        conversation_context=conversation_context,
    )
    return ask_model_func(prompt)