import re


def extract_parameters(user_input: str, skill_name: str) -> dict:
    text = user_input.strip()
    lower = text.lower()

    if skill_name == "book_ride":
        return _extract_ride_params(text, lower)

    if skill_name == "order_food":
        return _extract_food_params(text, lower)

    if skill_name == "book_show":
        return _extract_show_params(text, lower)

    if skill_name == "call_person":
        return _extract_call_params(text, lower)

    if skill_name == "send_whatsapp":
        return _extract_whatsapp_params(text, lower)

    if skill_name == "send_email":
        return _extract_email_params(text, lower)

    return {}


def _extract_ride_params(text: str, lower: str) -> dict:
    params = {}

    match = re.search(
        r'book(?: me)?(?: a)? ride from\s+(.+?)\s+to\s+(.+?)(?:\s+at\s+(.+))?$',
        text,
        re.IGNORECASE
    )
    if match:
        params["pickup"] = match.group(1).strip()
        params["destination"] = match.group(2).strip()
        if match.group(3):
            params["time"] = match.group(3).strip()
        return params

    match = re.search(
        r'from\s+(.+?)\s+to\s+(.+?)(?:\s+at\s+(.+))?$',
        text,
        re.IGNORECASE
    )
    if match:
        params["pickup"] = match.group(1).strip()
        params["destination"] = match.group(2).strip()
        if match.group(3):
            params["time"] = match.group(3).strip()
        return params

    from_only = re.search(r'from\s+(.+)', text, re.IGNORECASE)
    to_only = re.search(r'to\s+(.+)', text, re.IGNORECASE)
    time_match = re.search(r'at\s+([a-zA-Z0-9: ]+)', text, re.IGNORECASE)

    if from_only:
        params["pickup"] = from_only.group(1).strip()

    if to_only:
        params["destination"] = to_only.group(1).strip()

    if time_match:
        params["time"] = time_match.group(1).strip()

    return params


def _extract_food_params(text: str, lower: str) -> dict:
    params = {}

    match = re.search(r'order\s+(.+?)\s+from\s+(.+)', text, re.IGNORECASE)
    if match:
        params["item_or_cuisine"] = match.group(1).strip()
        params["restaurant"] = match.group(2).strip()
        return params

    match = re.search(r'get\s+(.+?)\s+from\s+(.+)', text, re.IGNORECASE)
    if match:
        params["item_or_cuisine"] = match.group(1).strip()
        params["restaurant"] = match.group(2).strip()
        return params

    match = re.search(r'buy\s+(.+?)\s+from\s+(.+)', text, re.IGNORECASE)
    if match:
        params["item_or_cuisine"] = match.group(1).strip()
        params["restaurant"] = match.group(2).strip()
        return params

    match = re.search(r'(.+?)\s+from\s+(.+)', text, re.IGNORECASE)
    if match:
        left = match.group(1).strip()
        right = match.group(2).strip()

        fillers = ["order", "get", "buy", "me", "for me", "please"]
        for filler in fillers:
            if left.lower().startswith(filler + " "):
                left = left[len(filler):].strip()

        if left:
            params["item_or_cuisine"] = left
        if right:
            params["restaurant"] = right
        return params

    match = re.search(r'(?:order|get|buy)\s+(.+)', text, re.IGNORECASE)
    if match:
        params["item_or_cuisine"] = match.group(1).strip()
        return params

    return params


def _extract_show_params(text: str, lower: str) -> dict:
    params = {}

    match = re.search(r'book show for\s+(.+)', text, re.IGNORECASE)
    if match:
        params["show_name"] = match.group(1).strip()
        return params

    match = re.search(r'book movie for\s+(.+)', text, re.IGNORECASE)
    if match:
        params["show_name"] = match.group(1).strip()
        return params

    if "movie" in lower or "show" in lower:
        cleaned = re.sub(r'book show|book movie|movie|show', '', text, flags=re.IGNORECASE).strip()
        if cleaned:
            params["show_name"] = cleaned

    return params


def _extract_call_params(text: str, lower: str) -> dict:
    params = {}

    match = re.search(r'call\s+(.+)', text, re.IGNORECASE)
    if match:
        params["person"] = match.group(1).strip()

    return params


def _extract_whatsapp_params(text: str, lower: str) -> dict:
    params = {}

    patterns = [
        r'send whatsapp to\s+(.+?)\s+saying\s+(.+)',
        r'whatsapp\s+(.+?)\s+saying\s+(.+)',
        r'send message to\s+(.+?)\s+saying\s+(.+)',
        r'message\s+(.+?)\s+saying\s+(.+)',
        r'reply to\s+(.+?)\s+saying\s+(.+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            params["person"] = match.group(1).strip()
            params["message"] = match.group(2).strip()
            return params

    to_match = re.search(r'to\s+(.+)', text, re.IGNORECASE)
    if to_match:
        params["person"] = to_match.group(1).strip()

    return params


def _extract_email_params(text: str, lower: str) -> dict:
    params = {}

    patterns = [
        r'send email to\s+(.+?)\s+saying\s+(.+)',
        r'email\s+(.+?)\s+saying\s+(.+)',
        r'mail\s+(.+?)\s+saying\s+(.+)'
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            params["person"] = match.group(1).strip()
            params["message"] = match.group(2).strip()
            return params

    return params