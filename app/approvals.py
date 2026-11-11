SENSITIVE_KEYWORDS = [
    "order",
    "buy",
    "book",
    "ride",
    "food",
    "show",
    "send",
    "call",
    "pay",
    "purchase"
]


def needs_approval(user_text: str) -> bool:
    return any(word in user_text.lower() for word in SENSITIVE_KEYWORDS)