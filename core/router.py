from skills.registry import SKILL_REGISTRY
from core.session_manager import has_active_session, is_awaiting_approval, is_awaiting_final_approval


def classify_request(user_input: str) -> dict:
    text = user_input.lower().strip()

    if is_awaiting_final_approval():
        if text in ["final approve", "confirm order", "place order"]:
            return {"mode": "final_approval", "action": "confirm"}

    if is_awaiting_approval():
        if text in ["approve", "yes", "confirm", "go ahead", "do it"]:
            return {"mode": "approval", "action": "approve"}

        if text in ["cancel", "no", "stop", "reject"]:
            return {"mode": "approval", "action": "cancel"}

    if has_active_session():
        return {"mode": "tool_followup", "action": "continue_skill"}

    # Rule mode
    if text == "/test":
        return {"mode": "rule", "action": "test"}

    if text in ["hello", "hi", "hey"]:
        return {"mode": "rule", "action": "greeting"}

    if "what food do i like" in text or "what is my favorite food" in text:
        return {"mode": "rule", "action": "memory_lookup"}

    if "who are you" in text:
        return {"mode": "rule", "action": "identity"}

    # Strong food detection first
    food_patterns = [
        "order ",
        "get ",
        "buy ",
        "biryani",
        "pizza",
        "burger",
        "dosa",
        "momos",
        "sev tamatar",
        "food from",
    ]
    for pattern in food_patterns:
        if pattern in text:
            return {"mode": "tool", "action": "order_food"}

    # Strong WhatsApp detection
    whatsapp_patterns = [
        "send whatsapp",
        "whatsapp",
        "message on whatsapp",
        "send message to",
        "message mom",
        "message dad",
        "reply to mom",
        "reply to mother",
        "reply on whatsapp"
    ]
    for pattern in whatsapp_patterns:
        if pattern in text:
            return {"mode": "tool", "action": "send_whatsapp"}

    # Tool mode fallback from registry
    for skill_name, skill_info in SKILL_REGISTRY.items():
        for keyword in skill_info["keywords"]:
            if keyword in text:
                return {"mode": "tool", "action": skill_name}

    return {"mode": "brain", "action": "chat"}