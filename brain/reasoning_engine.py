from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class ReasoningResult:
    mode: str
    problem_type: str
    goal: str
    confidence: float
    should_plan: bool
    should_execute_directly: bool
    needs_research: bool
    needs_tools: bool
    needs_memory: bool
    urgency: str
    subgoals: list[str]
    risks: list[str]
    notes: list[str]


def normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def strip_debug_suffix(text: str) -> str:
    raw = (text or "").strip()
    if raw.lower().endswith(" debug"):
        return raw[:-6].strip()
    return raw


def _contains_any(text: str, words: list[str]) -> bool:
    return any(word in text for word in words)


def _extract_goal(user_input: str) -> str:
    text = (user_input or "").strip()
    low = normalize(text)

    prefixes = [
        "krishna, ",
        "krishna ",
        "please ",
        "can you ",
        "could you ",
        "i want you to ",
        "help me ",
    ]

    for prefix in prefixes:
        if low.startswith(prefix.strip()):
            return text[len(prefix):].strip()

    return text


def _infer_subgoals(user_input: str, mode: str) -> list[str]:
    if mode == "research":
        return [
            "Clarify the research focus",
            "Gather relevant information",
            "Compare important points",
            "Synthesize findings into a clear answer",
        ]

    if mode == "task":
        return [
            "Understand the goal",
            "Break into steps",
            "Execute safely",
            "Verify result",
        ]

    return []


def _infer_risks(mode: str) -> list[str]:
    if mode == "research":
        return ["Available source material may be incomplete or mixed in quality."]
    if mode == "task":
        return ["Task scope may expand beyond initial request."]
    return []


def think(user_input: str) -> ReasoningResult:
    clean_input = strip_debug_suffix(user_input)
    text = normalize(clean_input)
    goal = _extract_goal(clean_input)

    mode = "conversation"
    problem_type = "general"
    confidence = 0.7
    should_plan = False
    should_execute_directly = False
    needs_research = False
    needs_tools = False
    needs_memory = False
    urgency = "normal"
    notes: list[str] = []

    # 🔥 RESEARCH PRIORITY
    research_keywords = [
        "research",
        "compare",
        "analyze",
        "analyse",
        "evaluate",
        "pros and cons",
        "difference between",
        "which is better",
    ]

    if _contains_any(text, research_keywords):
        mode = "research"
        problem_type = "research"
        should_plan = True
        needs_research = True
        confidence = 0.95
        notes.append("Research request detected.")

    # ⚙️ TASK ONLY IF EXPLICIT
    if "take it from here" in text:
        mode = "task"
        problem_type = "autonomous_task"
        should_plan = True
        confidence = 0.98
        notes.append("Explicit task ownership.")

    subgoals = _infer_subgoals(clean_input, mode)
    risks = _infer_risks(mode)

    return ReasoningResult(
        mode=mode,
        problem_type=problem_type,
        goal=goal,
        confidence=confidence,
        should_plan=should_plan,
        should_execute_directly=should_execute_directly,
        needs_research=needs_research,
        needs_tools=needs_tools,
        needs_memory=needs_memory,
        urgency=urgency,
        subgoals=subgoals,
        risks=risks,
        notes=notes,
    )


def summarize_reasoning(result: ReasoningResult) -> dict[str, Any]:
    return asdict(result)