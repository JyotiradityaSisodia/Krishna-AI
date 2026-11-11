from __future__ import annotations

from typing import Any, Dict

from brain.journal import log_entry


def install_voice_module() -> dict[str, Any]:
    try:
        from brain.voice_listener import listen  # import check only

        _ = listen  # silence unused warning

        return {
            "ability": "voice recognition",
            "result": "installed",
            "next_step": "use 'listen now' in chat to test microphone transcription",
            "message": "Voice module installed successfully using Faster-Whisper + Silero VAD.",
        }
    except Exception as e:
        return {
            "ability": "voice recognition",
            "result": "failed",
            "message": f"Voice module installation failed: {e}",
        }


def install_face_module() -> dict[str, Any]:
    return {
        "ability": "face recognition",
        "result": "installed_stub",
        "next_step": "connect webcam + face verification pipeline",
        "message": "Face recognition module stub installed successfully.",
    }


def install_memory_module() -> dict[str, Any]:
    return {
        "ability": "memory",
        "result": "installed_stub",
        "next_step": "connect persistent memory store into chat flow",
        "message": "Memory module stub installed successfully.",
    }


def install_communication_module() -> dict[str, Any]:
    return {
        "ability": "communication",
        "result": "installed_stub",
        "next_step": "wire message triage / call handling modules",
        "message": "Communication module stub installed successfully.",
    }


def install_general_module(ability: str) -> dict[str, Any]:
    return {
        "ability": ability,
        "result": "planned_only",
        "next_step": "no concrete installer yet",
        "message": f"No concrete installer exists yet for '{ability}'. Plan created only.",
    }


def _select_installer(plan: Dict[str, Any]):
    ability = str(plan.get("ability", "")).lower()
    category = str(plan.get("category", "")).lower()

    if "voice" in ability or category == "voice":
        return install_voice_module

    if "face" in ability or category == "security":
        return install_face_module

    if "memory" in ability or category == "memory":
        return install_memory_module

    if category == "communication" or any(
        word in ability for word in ["call", "message", "notification", "text"]
    ):
        return install_communication_module

    return None


def handle_listen() -> dict[str, Any]:
    try:
        from brain.voice_listener import listen

        text = listen()

        if not text or len(text.strip()) < 2:
            return {
                "success": False,
                "message": "Didn't catch that. Please speak again.",
            }

        return {
            "success": True,
            "heard": text,
            "message": "Voice input processed successfully.",
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Voice system error.",
        }


def execute_upgrade(plan: Dict[str, Any]) -> Dict[str, Any]:
    ability = str(plan.get("ability", "")).strip()
    risk = str(plan.get("risk", "unknown")).lower()

    if not ability:
        result = {
            "ability": ability,
            "result": "failed",
            "message": "No ability provided for execution.",
        }

        log_entry(
            category="upgrade_execution",
            task="execute_unknown_upgrade",
            result="failed",
            reason="Missing ability name",
            notes="Executor was called without a valid ability.",
            priority="high",
            metadata=plan,
        )
        return result

    installer = _select_installer(plan)

    try:
        if installer is None:
            execution = install_general_module(ability)
        else:
            execution = installer()

        final_result = str(execution.get("result", "unknown")).lower()

        if final_result in {"installed_stub", "success", "installed"}:
            journal_result = "success"
        elif final_result in {"planned_only"}:
            journal_result = "pending"
        else:
            journal_result = "failed"

        log_entry(
            category="upgrade_execution",
            task=f"execute_{ability}",
            result=journal_result,
            reason=f"Execution attempted for '{ability}'",
            notes=f"Risk={risk}; ExecutorResult={final_result}",
            priority="high" if risk == "high" else "normal",
            metadata={
                "plan": plan,
                "execution": execution,
            },
        )

        return execution

    except Exception as e:
        result = {
            "ability": ability,
            "result": "failed",
            "message": f"Upgrade '{ability}' execution failed: {e}",
        }

        log_entry(
            category="upgrade_execution",
            task=f"execute_{ability}",
            result="failed",
            reason="Executor raised an exception",
            notes=str(e),
            priority="high",
            metadata=plan,
        )

        return result