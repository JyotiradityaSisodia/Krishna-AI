from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from brain.advisor import suggest_next
from brain.decision_engine import proactive_suggestion, quick_reply, smart_decision
from brain.executor import execute_upgrade
from brain.intent_engine import classify_intent
from brain.memory_store import (
    add_memory,
    build_memory_context,
    remove_memory,
    summarize_memory,
)
from brain.reasoning_engine import think, summarize_reasoning
from brain.research_mode import (
    format_research_reply,
    is_research_request,
    run_research,
)
from brain.response_guard import (
    build_safe_prompt,
    is_bad_input,
    jarvisify_reply,
    safe_wake_reply,
    sanitize_reply,
)
from brain.self_improvement import (
    handle_self_improvement,
    should_handle_self_improvement,
)
from brain.task_engine import (
    advance_current_task_step,
    clear_completed_tasks,
    complete_current_task,
    execute_task_now,
    explain_current_task,
    format_task_plan_for_reply,
    pause_current_task,
    reset_all_tasks,
    resume_current_task,
    summarize_active_tasks,
    update_current_task_progress,
)
from brain.tool_system import execute_tool
from brain.upgrade_manager import request_upgrade
from brain.conversation_store import add_turn, get_recent_context
from brain.long_term_memory import store_conversation, search_memory
from brain.web_retrieval import (
    direct_web_answer,
    retrieve_and_analyze,
    should_use_web,
)
from core.orchestrator import ask_model

app = FastAPI(title="Krishna Chat Backend")

# CORS for local frontend testing / future UI integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: object


def wants_debug(user_input: str) -> bool:
    text = (user_input or "").strip().lower()
    debug_triggers = [
        "debug",
        "show reasoning",
        "show plan json",
        "show task json",
        "developer mode",
        "verbose mode",
    ]
    return any(trigger in text for trigger in debug_triggers)


def is_deeper_followup(user_input: str) -> bool:
    text = (user_input or "").strip().lower()
    triggers = {
        "yes",
        "yes please",
        "go deeper",
        "explain further",
        "tell me more",
        "go in detail",
        "go into detail",
        "deeper breakdown",
        "expand on that",
        "continue",
    }
    return text in triggers


def get_last_user_question_from_context(conversation_context: str) -> str:
    lines = [line.strip() for line in (
        conversation_context or "").splitlines() if line.strip()]
    for line in reversed(lines):
        low = line.lower()
        if low.startswith("user:"):
            return line.split(":", 1)[1].strip()
    return ""


@app.get("/")
def root():
    return {"message": "Krishna chat backend is running"}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    user_input = (req.message or "").strip()
    debug_mode = wants_debug(user_input)

    if not user_input:
        return ChatResponse(response="How can I help you, sir?")

    conversation_context = get_recent_context()
    lowered = user_input.lower().strip()

    if is_deeper_followup(user_input):
        last_question = get_last_user_question_from_context(
            conversation_context)
        if last_question:
            user_input = f"Explain this in more detail with a deeper breakdown: {last_question}"
            lowered = user_input.lower().strip()

    fast = quick_reply(user_input)
    if fast:
        add_turn("user", user_input)
        add_turn("assistant", fast)
        store_conversation(user_input, fast)
        return ChatResponse(response=fast)

    wake = safe_wake_reply(user_input)
    if wake:
        add_turn("user", user_input)
        add_turn("assistant", wake)
        store_conversation(user_input, wake)
        return ChatResponse(response=wake)

    if is_bad_input(user_input):
        return ChatResponse(response="I did not catch that clearly, sir.")

    # Self-improvement loop
    if should_handle_self_improvement(user_input):
        reply = handle_self_improvement(user_input)
        add_turn("user", user_input)
        add_turn("assistant", str(reply))
        store_conversation(user_input, str(reply))
        return ChatResponse(response=reply)

    # Hard command routing
    if lowered in {"show active tasks", "task status", "what are your active tasks"}:
        reply = summarize_active_tasks()
        add_turn("user", user_input)
        add_turn("assistant", reply)
        store_conversation(user_input, reply)
        return ChatResponse(response=reply)

    if lowered in {"what are you working on", "current task", "what are you doing"}:
        reply = explain_current_task()
        add_turn("user", user_input)
        add_turn("assistant", reply)
        store_conversation(user_input, reply)
        return ChatResponse(response=reply)

    if lowered in {"resume current task", "resume task", "resume that task"}:
        reply = resume_current_task()
        add_turn("user", user_input)
        add_turn("assistant", reply)
        store_conversation(user_input, reply)
        return ChatResponse(response=reply)

    if lowered in {"pause current task", "pause task", "pause that task"}:
        reply = pause_current_task()
        add_turn("user", user_input)
        add_turn("assistant", reply)
        store_conversation(user_input, reply)
        return ChatResponse(response=reply)

    if lowered in {"mark task complete", "complete current task", "complete task"}:
        reply = complete_current_task()
        add_turn("user", user_input)
        add_turn("assistant", reply)
        store_conversation(user_input, reply)
        return ChatResponse(response=reply)

    if lowered in {"clear completed tasks"}:
        reply = clear_completed_tasks()
        add_turn("user", user_input)
        add_turn("assistant", reply)
        store_conversation(user_input, reply)
        return ChatResponse(response=reply)

    if lowered in {"clear tasks", "reset tasks", "clear active tasks", "clear all tasks"}:
        reply = reset_all_tasks()
        add_turn("user", user_input)
        add_turn("assistant", reply)
        store_conversation(user_input, reply)
        return ChatResponse(response=reply)

    if lowered.startswith("progress:"):
        note = user_input.split(":", 1)[1].strip()
        reply = update_current_task_progress(note)
        add_turn("user", user_input)
        add_turn("assistant", reply)
        store_conversation(user_input, reply)
        return ChatResponse(response=reply)

    if lowered in {"advance current step", "next task step", "complete current step"}:
        reply = advance_current_task_step()
        add_turn("user", user_input)
        add_turn("assistant", reply)
        store_conversation(user_input, reply)
        return ChatResponse(response=reply)

    reasoning = think(user_input)

    # RESEARCH MUST WIN BEFORE TASK MODE
    if is_research_request(user_input) or reasoning.mode == "research":
        research_result = run_research(user_input)
        reply = format_research_reply(research_result)
        reply = sanitize_reply(reply, user_input)
        reply = jarvisify_reply(user_input, reply)

        add_turn("user", user_input)
        add_turn("assistant", reply)
        store_conversation(user_input, reply)

        if debug_mode:
            return ChatResponse(
                response={
                    "route": "research",
                    "assistant_reply": reply,
                    "reasoning": summarize_reasoning(reasoning),
                    "research_result": research_result,
                }
            )

        return ChatResponse(response=reply)

    if reasoning.mode == "tool":
        tool_reply = execute_tool(user_input)
        if tool_reply:
            add_turn("user", user_input)
            add_turn("assistant", tool_reply)
            store_conversation(user_input, tool_reply)

            if debug_mode:
                return ChatResponse(
                    response={
                        "route": "tool",
                        "assistant_reply": tool_reply,
                        "reasoning": summarize_reasoning(reasoning),
                    }
                )
            return ChatResponse(response=tool_reply)

    # Task mode only on explicit ownership
    if "take it from here" in lowered:
        task_result = execute_task_now(user_input)
        reply = format_task_plan_for_reply(task_result)

        add_turn("user", user_input)
        add_turn("assistant", reply)
        store_conversation(user_input, reply)

        if debug_mode:
            return ChatResponse(
                response={
                    "route": "task",
                    "assistant_reply": reply,
                    "reasoning": summarize_reasoning(reasoning),
                    "task_result": task_result,
                }
            )

        return ChatResponse(response=reply)

    intent_data = classify_intent(user_input)
    intent = intent_data["intent"]
    entities = intent_data.get("entities", {})

    if intent == "memory_add_fact":
        reply = add_memory("facts", entities.get("content", ""))
        add_turn("user", user_input)
        add_turn("assistant", reply)
        store_conversation(user_input, reply)
        return ChatResponse(response=reply)

    if intent == "memory_show":
        reply = summarize_memory()
        add_turn("user", user_input)
        add_turn("assistant", reply)
        store_conversation(user_input, reply)
        return ChatResponse(response=reply)

    if intent == "memory_forget":
        reply = remove_memory(entities.get("content", ""))
        add_turn("user", user_input)
        add_turn("assistant", reply)
        store_conversation(user_input, reply)
        return ChatResponse(response=reply)

    if intent == "upgrade_request":
        reply = request_upgrade(entities.get("ability", ""))
        add_turn("user", user_input)
        add_turn("assistant", reply)
        store_conversation(user_input, reply)
        return ChatResponse(response=reply)

    if intent == "upgrade_approve":
        reply = execute_upgrade(
            {"ability": entities.get("ability", ""), "risk": "medium"})
        add_turn("user", user_input)
        add_turn("assistant", reply)
        store_conversation(user_input, reply)
        return ChatResponse(response=reply)

    if intent == "advisor_next_step":
        reply = suggest_next()
        add_turn("user", user_input)
        add_turn("assistant", reply)
        store_conversation(user_input, reply)
        return ChatResponse(response=reply)

    decision = smart_decision(user_input, intent)
    if decision["action"] == "direct_reply" and decision["reply"]:
        reply = decision["reply"]
        add_turn("user", user_input)
        add_turn("assistant", reply)
        store_conversation(user_input, reply)
        return ChatResponse(response=reply)

    memory_context = build_memory_context()
    long_memory = search_memory(user_input)

    use_web = should_use_web(user_input)

    # BLOCK web for simple explanations
    simple_explanation_triggers = [
        "explain",
        "what is",
        "what are",
        "define",
        "meaning of",
        "tell me about",
    ]
    if any(trigger in lowered for trigger in simple_explanation_triggers):
        use_web = False

    web_context = retrieve_and_analyze(user_input) if use_web else ""

    prompt = build_safe_prompt(
        user_input=user_input,
        memory_context=memory_context,
        conversation_context=conversation_context,
        long_memory=long_memory,
        web_context=web_context,
    )

    raw = ask_model(prompt)
    safe = sanitize_reply(str(raw), user_input)

    if safe in {"Understood.", "I did not catch that clearly."} and not use_web:
        safe = "I am having trouble generating a full reply right now. Please try again in a moment."

    final = jarvisify_reply(user_input, safe)

    if use_web and final.lower().startswith("understood"):
        web_answer = direct_web_answer(user_input)
        if web_answer and "could not retrieve enough reliable information" not in web_answer.lower():
            final = web_answer

    pro = proactive_suggestion(user_input)
    if pro and len(final) < 150:
        final += " " + pro

    add_turn("user", user_input)
    add_turn("assistant", final)
    store_conversation(user_input, final)

    if debug_mode:
        return ChatResponse(
            response={
                "route": "chat",
                "assistant_reply": final,
                "reasoning": summarize_reasoning(reasoning),
            }
        )

    return ChatResponse(response=final)
