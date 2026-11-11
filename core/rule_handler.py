from app.memory import get_memory_by_key, log_task


def handle_rule(action: str, user_input: str) -> str:
    if action == "test":
        return "Krishna test mode is working."

    if action == "greeting":
        return "Hello. I am Krishna. How can I help you today?"

    if action == "identity":
        return "I am Krishna, your personal AI assistant."

    if action == "memory_lookup":
        memory = get_memory_by_key("food") or get_memory_by_key("favorite_food")
        if memory:
            reply = f"You told me your food preference is {memory['value']}."
            log_task(user_input, reply)
            return reply
        return "You have not told me your food preference yet."

    return "I could not handle that rule request."