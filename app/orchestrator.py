import requests
from app.memory import get_memory_by_key, log_task
from app.config import OLLAMA_URL, MODEL_NAME, BACKEND_TIMEOUT


def ask_model(user_input: str):
    text = user_input.lower().strip()

    if text == "/test":
        return "Krishna test mode is working."

    if "what food do i like" in text or "what is my favorite food" in text:
        memory = get_memory_by_key("food") or get_memory_by_key("favorite_food")
        if memory:
            reply = f"You told me your food preference is {memory['value']}."
            log_task(user_input, reply)
            return reply

    try:
        res = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "messages": [
                    {"role": "user", "content": user_input}
                ],
                "stream": False
            },
            timeout=BACKEND_TIMEOUT
        )

        if not res.ok:
            return f"Krishna error: Ollama returned {res.status_code}: {res.text}"

        data = res.json()
        reply = data.get("message", {}).get("content", "No reply received.")
        log_task(user_input, reply)
        return reply

    except requests.exceptions.Timeout:
        return "Krishna error: backend timed out waiting for Ollama."
    except Exception as e:
        return f"Krishna error: {str(e)}"