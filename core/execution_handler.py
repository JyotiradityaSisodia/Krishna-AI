from skills.registry import SKILL_REGISTRY
from core.session_manager import get_session, clear_session, clear_approval_state


def execute_current_skill() -> str:
    session = get_session()
    skill_name = session["active_skill"]

    if not skill_name:
        return "There is no active skill to execute."

    skill_info = SKILL_REGISTRY.get(skill_name)
    if not skill_info:
        clear_session()
        return f"Skill '{skill_name}' not found."

    handler = skill_info["handler"]

    try:
        result = handler.execute(session["params"], session)

        clear_approval_state()
        clear_session()

        return result.get("message", "Skill executed successfully.")

    except Exception as e:
        clear_approval_state()
        clear_session()
        return f"Execution error in skill '{skill_name}': {str(e)}"


def cancel_current_skill() -> str:
    session = get_session()
    active_skill = session["active_skill"]

    if not active_skill:
        return "There is no active skill to cancel."

    clear_session()
    return f"Cancelled skill '{active_skill}'."