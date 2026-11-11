from __future__ import annotations

from typing import Any

from brain.journal import get_recent, summarize_recent, get_failure_entries


def _top_failure_tasks(entries: list[dict[str, Any]]) -> list[tuple[str, int]]:
    counts: dict[str, int] = {}

    for entry in entries:
        task = str(entry.get("task", "")).strip()
        if not task:
            continue
        counts[task] = counts.get(task, 0) + 1

    ranked = sorted(counts.items(), key=lambda x: x[1], reverse=True)
    return ranked


def analyze() -> dict[str, Any]:
    summary = summarize_recent(20)
    recent = summary["recent"]
    failures = [
        entry for entry in recent
        if str(entry.get("result", "")).lower() == "failed"
    ]
    pending = [
        entry for entry in recent
        if str(entry.get("result", "")).lower() == "pending"
    ]
    successes = [
        entry for entry in recent
        if str(entry.get("result", "")).lower() == "success"
    ]

    top_failures = _top_failure_tasks(failures)

    if len(failures) >= 4:
        main_task = top_failures[0][0] if top_failures else "current workflow"
        return {
            "priority": "HIGH",
            "status": "pivot_recommended",
            "recommendation": f"Pause or redesign '{main_task}' before spending more time on it.",
            "reason": f"{len(failures)} recent failures were detected.",
            "top_failure_tasks": top_failures[:5],
            "pending_count": len(pending),
            "success_count": len(successes),
        }

    if len(pending) >= 3 and len(successes) == 0:
        return {
            "priority": "MEDIUM",
            "status": "finish_in_progress_work",
            "recommendation": "Too many pending changes exist. Finish and verify current work before adding more.",
            "reason": f"{len(pending)} recent items are still pending.",
            "top_failure_tasks": top_failures[:5],
            "pending_count": len(pending),
            "success_count": len(successes),
        }

    if len(successes) >= 2 and len(failures) <= 1:
        return {
            "priority": "LOW",
            "status": "continue",
            "recommendation": "Current direction looks stable. Continue with the next planned improvement.",
            "reason": f"{len(successes)} recent successes and low failure rate detected.",
            "top_failure_tasks": top_failures[:5],
            "pending_count": len(pending),
            "success_count": len(successes),
        }

    return {
        "priority": "MEDIUM",
        "status": "stabilize",
        "recommendation": "Stabilize the current layer before expanding scope.",
        "reason": "The system is moving, but not stable enough for aggressive expansion yet.",
        "top_failure_tasks": top_failures[:5],
        "pending_count": len(pending),
        "success_count": len(successes),
    }


def suggest_next() -> str:
    analysis = analyze()
    rec = analysis["recommendation"]
    reason = analysis["reason"]
    priority = analysis["priority"]

    return (
        f"Priority: {priority}. {rec} Reason: {reason}"
    )


def builder_brief() -> dict[str, Any]:
    analysis = analyze()
    recent_failures = get_failure_entries(10)

    return {
        "analysis": analysis,
        "recent_failures": recent_failures,
        "next_message": suggest_next(),
    }
