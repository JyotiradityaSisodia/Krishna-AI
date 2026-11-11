from __future__ import annotations

from typing import Any

from brain.web_retrieval import retrieve_and_analyze, should_use_web
from core.orchestrator import ask_research_model


def strip_debug_suffix(text: str) -> str:
    raw = (text or "").strip()
    if raw.lower().endswith(" debug"):
        return raw[:-6].strip()
    return raw


def is_research_request(user_input: str) -> bool:
    text = user_input.lower()

    triggers = [
        "research",
        "compare",
        "analyze",
        "analyse",
        "pros and cons",
        "difference between",
        "which is better",
    ]

    return any(trigger in text for trigger in triggers)


def run_research(user_input: str) -> dict[str, Any]:
    clean_query = strip_debug_suffix(user_input)

    use_web = should_use_web(clean_query)

    source_material = ""
    if use_web:
        source_material = retrieve_and_analyze(clean_query)

    if not source_material:
        source_material = "Use general knowledge and reasoning."

    answer = ask_research_model(clean_query, source_material)

    return {
        "query": clean_query,
        "used_web": use_web,
        "source_material": source_material,
        "answer": answer,
    }


def format_research_reply(result: dict[str, Any]) -> str:
    return (result.get("answer") or "").strip()