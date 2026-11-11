from __future__ import annotations

from typing import Any

from brain.self_improvement_store import (
    add_idea,
    clear_ideas,
    get_idea_by_id,
    get_latest_pending_idea,
    list_ideas,
    update_idea_status,
)
from brain.task_engine import execute_task_now, format_task_plan_for_reply


def normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def should_handle_self_improvement(user_input: str) -> bool:
    text = normalize(user_input)

    triggers = [
        "improve yourself",
        "upgrade yourself",
        "self improvement",
        "self-improvement",
        "improvement idea",
        "upgrade idea",
        "propose an upgrade",
        "suggest an upgrade",
        "what should you improve",
        "what can you improve",
        "list upgrade ideas",
        "show upgrade ideas",
        "approve latest upgrade",
        "reject latest upgrade",
        "clear upgrade ideas",
    ]

    return any(trigger in text for trigger in triggers)


def _extract_manual_idea(text: str) -> tuple[str, str]:
    raw = (text or "").strip()

    for prefix in [
        "improvement idea:",
        "upgrade idea:",
        "self improvement idea:",
        "self-improvement idea:",
    ]:
        if raw.lower().startswith(prefix):
            content = raw[len(prefix):].strip()
            return content, content

    return "", ""


def handle_self_improvement(user_input: str) -> str | dict[str, Any]:
    text = normalize(user_input)
    raw = (user_input or "").strip()

    # Add explicit idea
    title, details = _extract_manual_idea(raw)
    if title:
        idea = add_idea(title=title, details=details, source="manual")
        return f"Upgrade idea recorded: {idea['title']}. Would you like me to turn it into a tracked task?"

    # Auto-suggested improvement prompts
    if any(trigger in text for trigger in ["what should you improve", "what can you improve", "suggest an upgrade", "propose an upgrade"]):
        suggested = add_idea(
            title="Improve Krishna's autonomous execution loop",
            details=(
                "Build the next stage of take-it-from-here behavior so Krishna can "
                "progress from planning into controlled execution, verification, and retry."
            ),
            source="krishna",
        )
        return (
            f"I propose this upgrade: {suggested['title']}. "
            "Would you like me to approve it and turn it into a tracked task?"
        )

    # List ideas
    if "list upgrade ideas" in text or "show upgrade ideas" in text:
        ideas = list_ideas()
        if not ideas:
            return "There are no stored upgrade ideas, sir."

        lines = []
        for idx, idea in enumerate(ideas[-10:], start=1):
            lines.append(
                f"{idx}. {idea.get('title', 'Untitled')} — {idea.get('status', 'unknown')} — source: {idea.get('source', 'unknown')}"
            )
        return "Upgrade ideas: " + " ".join(lines)

    # Approve latest
    if "approve latest upgrade" in text or "approve latest idea" in text:
        latest = get_latest_pending_idea()
        if not latest:
            return "There is no pending upgrade idea to approve, sir."

        update_idea_status(latest["id"], "approved")

        task_input = f"Build this upgrade for Krishna and take it from here: {latest['title']}. {latest.get('details', '')}"
        task_result = execute_task_now(task_input)
        task_reply = format_task_plan_for_reply(task_result)

        return (
            f"Approved upgrade: {latest['title']}. "
            f"{task_reply}"
        )

    # Reject latest
    if "reject latest upgrade" in text or "reject latest idea" in text:
        latest = get_latest_pending_idea()
        if not latest:
            return "There is no pending upgrade idea to reject, sir."

        update_idea_status(latest["id"], "rejected")
        return f"Rejected upgrade idea: {latest['title']}."

    # Approve by ID
    if text.startswith("approve upgrade "):
        idea_id = raw[len("approve upgrade "):].strip()
        idea = get_idea_by_id(idea_id)
        if not idea:
            return "I could not find that upgrade idea, sir."

        update_idea_status(idea_id, "approved")
        task_input = f"Build this upgrade for Krishna and take it from here: {idea['title']}. {idea.get('details', '')}"
        task_result = execute_task_now(task_input)
        task_reply = format_task_plan_for_reply(task_result)

        return (
            f"Approved upgrade: {idea['title']}. "
            f"{task_reply}"
        )

    # Reject by ID
    if text.startswith("reject upgrade "):
        idea_id = raw[len("reject upgrade "):].strip()
        idea = get_idea_by_id(idea_id)
        if not idea:
            return "I could not find that upgrade idea, sir."

        update_idea_status(idea_id, "rejected")
        return f"Rejected upgrade idea: {idea['title']}."

    # Clear
    if "clear upgrade ideas" in text:
        clear_ideas()
        return "All stored upgrade ideas have been cleared, sir."

    # Generic trigger
    if "improve yourself" in text or "upgrade yourself" in text:
        suggested = add_idea(
            title="Strengthen Krishna's real research mode",
            details=(
                "Build a true research workflow that gathers, compares, and synthesizes information "
                "instead of relying on a single-pass answer."
            ),
            source="krishna",
        )
        return (
            f"I have registered a self-improvement proposal: {suggested['title']}. "
            "Would you like me to approve it and convert it into a tracked task?"
        )

    return "I did not find a valid self-improvement action in that request, sir."