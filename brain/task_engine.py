from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Any

from brain.reasoning_engine import think
from brain.task_state import (
    add_task,
    clear_tasks,
    complete_task,
    get_active_tasks,
    get_current_task,
    get_next_open_step,
    mark_only_one_step_in_progress,
    pause_task,
    remove_completed_tasks,
    resume_task,
    update_task,
    update_task_step,
)
from brain.tool_system import execute_tool


@dataclass
class TaskStep:
    step: int
    title: str
    status: str
    details: str


@dataclass
class TaskPlan:
    goal: str
    mode: str
    summary: str
    steps: list[TaskStep]
    can_execute_now: bool
    execution_note: str
    risks: list[str]
    urgency: str
    subgoals: list[str]


def normalize(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def _contains_any(text: str, words: list[str]) -> bool:
    return any(word in text for word in words)


def _steps_from_subgoals(subgoals: list[str]) -> list[TaskStep]:
    return [
        TaskStep(step=i, title=subgoal, status="planned", details=subgoal)
        for i, subgoal in enumerate(subgoals, start=1)
    ]


def _build_default_research_steps() -> list[TaskStep]:
    return [
        TaskStep(1, "Clarify the research question", "planned", "Identify exactly what needs to be researched."),
        TaskStep(2, "Gather relevant information", "planned", "Collect useful source material and evidence."),
        TaskStep(3, "Compare and synthesize", "planned", "Find patterns, differences, and conclusions."),
        TaskStep(4, "Deliver structured findings", "planned", "Present a clear research-style answer."),
    ]


def _build_default_tool_steps() -> list[TaskStep]:
    return [
        TaskStep(1, "Interpret command", "planned", "Identify the requested direct action."),
        TaskStep(2, "Execute tool", "planned", "Use the correct tool immediately."),
        TaskStep(3, "Confirm result", "planned", "Report what was done."),
    ]


def _build_engineering_steps(text: str, subgoals: list[str]) -> list[TaskStep]:
    if subgoals:
        steps = _steps_from_subgoals(subgoals)
    else:
        steps = [
            TaskStep(1, "Understand the goal", "planned", "Clarify the desired end state."),
            TaskStep(2, "Break the work into sub-tasks", "planned", "Split the work into manageable steps."),
            TaskStep(3, "Choose implementation approach", "planned", "Select the most practical path."),
            TaskStep(4, "Execute carefully", "planned", "Implement changes safely and incrementally."),
            TaskStep(5, "Verify result", "planned", "Check whether the result actually works."),
        ]

    if _contains_any(text, ["fix", "debug", "repair", "error", "issue", "bug"]) and not any(
        "test" in s.title.lower() or "verify" in s.title.lower() for s in steps
    ):
        steps.append(
            TaskStep(
                step=len(steps) + 1,
                title="Test and debug",
                status="planned",
                details="Run checks, inspect errors, and refine the result.",
            )
        )

    if not any("verify" in s.title.lower() for s in steps):
        steps.append(
            TaskStep(
                step=len(steps) + 1,
                title="Verify result",
                status="planned",
                details="Confirm the result behaves as intended.",
            )
        )

    for idx, step in enumerate(steps, start=1):
        step.step = idx

    return steps


def build_task_plan(user_input: str) -> TaskPlan:
    reason = think(user_input)
    text = normalize(user_input)

    if reason.mode == "research":
        steps = _steps_from_subgoals(reason.subgoals) if reason.subgoals else _build_default_research_steps()
        return TaskPlan(
            goal=reason.goal,
            mode=reason.mode,
            summary="Research workflow prepared.",
            steps=steps,
            can_execute_now=True,
            execution_note="Can proceed through research and synthesis now.",
            risks=reason.risks,
            urgency=reason.urgency,
            subgoals=reason.subgoals,
        )

    if reason.mode == "tool":
        return TaskPlan(
            goal=reason.goal,
            mode=reason.mode,
            summary="Direct action task identified.",
            steps=_build_default_tool_steps(),
            can_execute_now=True,
            execution_note="Can execute immediately through the tool system.",
            risks=reason.risks,
            urgency=reason.urgency,
            subgoals=reason.subgoals,
        )

    if reason.mode in {"task", "advisor"} or reason.problem_type in {"engineering", "autonomous_task", "planning"}:
        return TaskPlan(
            goal=reason.goal,
            mode=reason.mode,
            summary="Structured execution plan prepared.",
            steps=_build_engineering_steps(text, reason.subgoals),
            can_execute_now=True,
            execution_note="Can start with bounded execution, planning, and verification.",
            risks=reason.risks,
            urgency=reason.urgency,
            subgoals=reason.subgoals,
        )

    return TaskPlan(
        goal=reason.goal,
        mode=reason.mode,
        summary="Normal conversational handling is sufficient.",
        steps=[
            TaskStep(1, "Answer directly", "planned", "Handle as a normal conversation or informational request.")
        ],
        can_execute_now=True,
        execution_note="No heavy task workflow needed.",
        risks=reason.risks,
        urgency=reason.urgency,
        subgoals=reason.subgoals,
    )


def _build_execution_record(user_input: str, plan: TaskPlan) -> dict[str, Any]:
    return {
        "id": f"task-{int(datetime.now().timestamp())}",
        "goal": plan.goal,
        "raw_input": user_input,
        "mode": plan.mode,
        "summary": plan.summary,
        "created_at": datetime.now().isoformat(),
        "status": "active",
        "urgency": plan.urgency,
        "subgoals": plan.subgoals,
        "risks": plan.risks,
        "steps": [asdict(step) for step in plan.steps],
        "execution_note": plan.execution_note,
        "last_progress_note": "",
    }


def _bounded_execution_reply(user_input: str, plan: TaskPlan) -> str:
    text = normalize(user_input)

    if plan.mode == "tool":
        reply = execute_tool(user_input)
        return reply or "I could not execute that action, sir."

    if plan.mode == "research":
        if plan.risks:
            return f"I have started the research workflow. Main caution: {plan.risks[0]}"
        return "I have started the research workflow, sir."

    if plan.mode in {"task", "advisor"}:
        if _contains_any(text, ["build", "create", "implement", "feature"]):
            return "I have taken ownership of the build task. I am starting with the goal, architecture, and execution plan."

        if _contains_any(text, ["fix", "debug", "repair", "error", "issue", "bug"]):
            return "I have taken ownership of the debugging task. I am starting by identifying the root cause before applying changes."

        if "take it from here" in text:
            return "I have taken ownership of the task. I will proceed with a structured plan and verify progress as I go."

        return "I have taken ownership of the task, sir."

    return "Understood."


def execute_task_now(user_input: str) -> dict[str, Any]:
    reason = think(user_input)

    if reason.should_execute_directly:
        tool_reply = execute_tool(user_input)
        if tool_reply is not None:
            return {
                "type": "executed",
                "goal": reason.goal,
                "reply": tool_reply,
                "reasoning_mode": reason.mode,
            }

    plan = build_task_plan(user_input)
    execution_record = _build_execution_record(user_input, plan)
    add_task(execution_record)

    if plan.steps:
        mark_only_one_step_in_progress(execution_record["id"], 1)

    assistant_reply = _bounded_execution_reply(user_input, plan)

    return {
        "type": "planned",
        "goal": plan.goal,
        "assistant_reply": assistant_reply,
        "plan": {
            "task_id": execution_record["id"],
            "goal": plan.goal,
            "mode": plan.mode,
            "summary": plan.summary,
            "steps": [asdict(step) for step in plan.steps],
            "can_execute_now": plan.can_execute_now,
            "execution_note": plan.execution_note,
            "risks": plan.risks,
            "urgency": plan.urgency,
            "subgoals": plan.subgoals,
        },
    }


def format_task_plan_for_reply(result: dict[str, Any]) -> str:
    if result["type"] == "executed":
        return str(result["reply"])

    if result.get("assistant_reply"):
        return str(result["assistant_reply"])

    plan = result["plan"]
    step_titles = [f"{s['step']}. {s['title']}" for s in plan["steps"][:4]]
    joined = " ".join(step_titles)

    risk_note = ""
    if plan.get("risks"):
        risk_note = f" Main caution: {plan['risks'][0]}"

    return f"I have taken ownership of the task. Plan: {plan['summary']} {joined}{risk_note}"


def summarize_active_tasks() -> str:
    tasks = [t for t in get_active_tasks() if t.get("status") != "completed"]
    if not tasks:
        return "There are no active tasks, sir."

    lines = []
    for idx, task in enumerate(tasks[-5:], start=1):
        goal = task.get("goal", "Unnamed task")
        status = task.get("status", "unknown")
        urgency = task.get("urgency", "normal")
        lines.append(f"{idx}. {goal} — {status} — urgency: {urgency}")

    return "Active tasks: " + " ".join(lines)


def explain_current_task() -> str:
    task = get_current_task()
    if not task:
        return "I am not actively working on a tracked task right now, sir."

    goal = task.get("goal", "Unnamed task")
    status = task.get("status", "unknown")
    next_step = get_next_open_step(task.get("id", ""))

    if next_step:
        return f"I am currently focused on: {goal}. Status: {status}. Current step: {next_step.get('title')}."
    return f"I am currently focused on: {goal}. Status: {status}."


def update_current_task_progress(progress_note: str) -> str:
    task = get_current_task()
    if not task:
        return "There is no current task to update, sir."

    task_id = task.get("id")
    if not task_id:
        return "The current task is missing an ID, sir."

    ok = update_task(task_id, {"last_progress_note": progress_note, "status": "active"})
    if not ok:
        return "I could not update the current task, sir."

    next_step = get_next_open_step(task_id)
    if next_step and next_step.get("status") == "planned":
        mark_only_one_step_in_progress(task_id, int(next_step["step"]))

    return f"Progress updated for the current task: {task.get('goal', 'Unnamed task')}."


def advance_current_task_step(note: str = "") -> str:
    task = get_current_task()
    if not task:
        return "There is no current task to advance, sir."

    task_id = task.get("id")
    if not task_id:
        return "The current task is missing an ID, sir."

    steps = task.get("steps", [])
    current_in_progress = None

    for step in steps:
        if step.get("status") == "in_progress":
            current_in_progress = step
            break

    if current_in_progress is None:
        next_step = get_next_open_step(task_id)
        if not next_step:
            return "There are no remaining steps to advance, sir."
        mark_only_one_step_in_progress(task_id, int(next_step["step"]))
        current_in_progress = next_step

    update_task_step(task_id, int(current_in_progress["step"]), {"status": "done"})

    next_step_number = int(current_in_progress["step"]) + 1
    found_next = False
    for step in steps:
        if int(step.get("step", -1)) == next_step_number:
            mark_only_one_step_in_progress(task_id, next_step_number)
            found_next = True
            break

    if note:
        update_task(task_id, {"last_progress_note": note})

    if found_next:
        next_step = get_next_open_step(task_id)
        return f"Step completed. Next step is: {next_step.get('title')}."

    complete_task(task_id)
    return "The current task has been completed, sir."


def resume_current_task() -> str:
    task = get_current_task()
    if task and task.get("status") in {"active", "paused"}:
        task_id = task.get("id")
        if task_id and resume_task(task_id):
            return f"I have resumed the current task: {task.get('goal', 'Unnamed task')}."

    tasks = [t for t in get_active_tasks() if t.get("status") in {"active", "paused"}]
    if not tasks:
        return "There is no paused or active task to resume, sir."

    latest = tasks[-1]
    task_id = latest.get("id")
    if task_id and resume_task(task_id):
        return f"I have resumed: {latest.get('goal', 'Unnamed task')}."

    return "I could not resume a task, sir."


def pause_current_task() -> str:
    task = get_current_task()
    if not task:
        return "There is no current task to pause, sir."

    task_id = task.get("id")
    if task_id and pause_task(task_id):
        return f"I have paused the current task: {task.get('goal', 'Unnamed task')}."

    return "I could not pause the current task, sir."


def complete_current_task() -> str:
    task = get_current_task()
    if not task:
        return "There is no current task to mark complete, sir."

    task_id = task.get("id")
    goal = task.get("goal", "Unnamed task")
    if task_id and complete_task(task_id):
        return f"I have marked the current task as complete: {goal}."

    return "I could not complete the current task, sir."


def clear_completed_tasks() -> str:
    removed = remove_completed_tasks()
    if removed == 0:
        return "There were no completed tasks to clear, sir."
    return f"I cleared {removed} completed task(s), sir."


def reset_all_tasks() -> str:
    clear_tasks()
    return "All task state has been cleared, sir."