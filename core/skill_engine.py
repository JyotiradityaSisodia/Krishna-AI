from skills.registry import SKILL_REGISTRY
from core.parameter_extractor import extract_parameters
from core.session_manager import (
    get_session,
    has_active_session,
    start_session,
    update_session_params,
    set_awaiting_approval
)


def run_skill_flow(user_input: str, skill_name: str | None = None) -> str:
    session = get_session()

    if has_active_session() and not skill_name:
        active_skill = session["active_skill"]
        params = extract_parameters(user_input, active_skill)
        update_session_params(params)

        handler = SKILL_REGISTRY[active_skill]["handler"]
        result = handler.run(session["params"], session)

        if result["status"] == "need_input":
            return result["message"]

        if result["status"] == "awaiting_approval":
            set_awaiting_approval(result["summary"])
            return result["message"] + f" Summary: {result['summary']}. Say 'approve' to continue or 'cancel' to stop."

        return result.get("message", "Skill completed.")

    if not skill_name:
        return "No skill selected."

    params = extract_parameters(user_input, skill_name)
    start_session(skill_name, params)

    session = get_session()
    handler = SKILL_REGISTRY[skill_name]["handler"]
    result = handler.run(session["params"], session)

    if result["status"] == "need_input":
        return result["message"]

    if result["status"] == "awaiting_approval":
        set_awaiting_approval(result["summary"])
        return result["message"] + f" Summary: {result['summary']}. Say 'approve' to continue or 'cancel' to stop."

    return result.get("message", "Skill completed.")