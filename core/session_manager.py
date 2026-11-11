CURRENT_SKILL_SESSION = {
    "active_skill": None,
    "params": {},
    "awaiting_approval": False,
    "pending_summary": None,
}


def get_session():
    return CURRENT_SKILL_SESSION


def start_session(skill_name: str, params: dict | None = None):
    CURRENT_SKILL_SESSION["active_skill"] = skill_name
    CURRENT_SKILL_SESSION["params"] = params or {}
    CURRENT_SKILL_SESSION["awaiting_approval"] = False
    CURRENT_SKILL_SESSION["pending_summary"] = None


def update_session_params(new_params: dict):
    CURRENT_SKILL_SESSION["params"].update(new_params)


def set_awaiting_approval(summary: dict):
    CURRENT_SKILL_SESSION["awaiting_approval"] = True
    CURRENT_SKILL_SESSION["pending_summary"] = summary


def clear_approval_state():
    CURRENT_SKILL_SESSION["awaiting_approval"] = False
    CURRENT_SKILL_SESSION["pending_summary"] = None


def clear_session():
    CURRENT_SKILL_SESSION["active_skill"] = None
    CURRENT_SKILL_SESSION["params"] = {}
    CURRENT_SKILL_SESSION["awaiting_approval"] = False
    CURRENT_SKILL_SESSION["pending_summary"] = None


def has_active_session() -> bool:
    return CURRENT_SKILL_SESSION["active_skill"] is not None


def is_awaiting_approval() -> bool:
    return CURRENT_SKILL_SESSION["awaiting_approval"] is True


CURRENT_SKILL_SESSION["awaiting_final_approval"] = False

def set_final_approval():
    CURRENT_SKILL_SESSION["awaiting_final_approval"] = True


def is_awaiting_final_approval():
    return CURRENT_SKILL_SESSION.get("awaiting_final_approval", False)


def clear_final_approval():
    CURRENT_SKILL_SESSION["awaiting_final_approval"] = False