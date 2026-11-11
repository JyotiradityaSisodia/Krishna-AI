from datetime import datetime


# Simple in-memory journal (later we persist)
upgrade_history = []


def request_upgrade(ability: str):
    """
    Called when user says:
    'learn voice recognition'
    """

    plan = {
        "success": True,
        "ability": ability,
        "category": detect_category(ability),
        "risk": estimate_risk(ability),
        "approval_required": True,
        "affected_modules": detect_modules(ability),
        "steps": [
            "Clarify the ability goal",
            "Research the best implementation path",
            "Prepare a patch plan",
            "Generate code changes",
            "Run tests and validation",
            "Apply only after approval if required",
            "Log the upgrade result",
        ],
        "message": f"Krishna received an upgrade request for '{ability}'.",
        "timestamp": datetime.utcnow().isoformat()
    }

    upgrade_history.append(plan)
    return plan


# -------------------------
# Helpers
# -------------------------

def detect_category(ability: str):
    ability = ability.lower()

    if "voice" in ability:
        return "voice"
    if "face" in ability:
        return "security"
    if "money" in ability or "income" in ability:
        return "finance"
    if "learn" in ability or "ai" in ability:
        return "intelligence"

    return "general"


def estimate_risk(ability: str):
    ability = ability.lower()

    if "face" in ability or "security" in ability:
        return "high"
    if "payment" in ability or "money" in ability:
        return "high"
    if "voice" in ability:
        return "medium"

    return "low"


def detect_modules(ability: str):
    ability = ability.lower()

    modules = ["brain/upgrade_manager.py"]

    if "voice" in ability:
        modules += ["android voice pipeline", "desktop voice pipeline"]

    if "face" in ability:
        modules += ["identity/auth modules", "permission system"]

    return modules
