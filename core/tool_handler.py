from skills.registry import SKILL_REGISTRY


def handle_tool(action: str) -> str:
    skill_info = SKILL_REGISTRY.get(action)

    if not skill_info:
        return f"Tool '{action}' not found."

    try:
        result = skill_info["handler"]()

        if isinstance(result, dict):
            return result.get("message", f"Skill '{action}' completed.")

        return str(result)

    except Exception as e:
        return f"Error while running tool '{action}': {str(e)}"