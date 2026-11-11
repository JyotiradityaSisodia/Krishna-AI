import json
import os
import urllib.request
import urllib.error


OLLAMA_BASE = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")
PREFERRED_MODELS = [
    os.getenv("KRISHNA_MODEL", "").strip(),
    "llama3.2:3b",
    "llama3.1:8b",
    "llama3",
    "mistral",
    "phi3",
]


def _http_json(url: str, payload: dict | None = None, timeout: int = 60) -> dict:
    data = None
    headers = {"Content-Type": "application/json"}

    if payload is not None:
        data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(url, data=data, headers=headers)

    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw)


def get_available_models() -> list[str]:
    try:
        data = _http_json(f"{OLLAMA_BASE}/api/tags", timeout=15)
        models = data.get("models", [])
        return [m.get("name", "") for m in models if m.get("name")]
    except Exception:
        return []


def choose_model() -> str | None:
    available = get_available_models()
    if not available:
        return None

    for model in PREFERRED_MODELS:
        if model and model in available:
            return model

    return available[0]


def build_prompt(user_text: str) -> str:
    system = (
        "You are Krishna, a calm, conversational, intelligent AI assistant. "
        "Speak naturally and clearly. "
        "Never mention internal tools, routing, missing skills, or code limitations. "
        "If the user asks a normal knowledge question, answer it directly and helpfully. "
        "If you are unsure, say so honestly in a clean way. "
        "Keep the tone polished, composed, and human-like."
    )

    return f"{system}\n\nUser: {user_text}\nKrishna:"


def generate_general_response(user_text: str) -> str:
    user_text = (user_text or "").strip()
    if not user_text:
        return "How can I help you?"

    model = choose_model()
    if not model:
        return (
            "I’m not able to reach my language model right now, but I’m still online. "
            "Start Ollama, and I’ll be able to answer general questions normally."
        )

    payload = {
        "model": model,
        "prompt": build_prompt(user_text),
        "stream": False,
    }

    try:
        result = _http_json(f"{OLLAMA_BASE}/api/generate", payload=payload, timeout=90)
        text = (result.get("response") or "").strip()

        if text:
            return text

        return "I’m here, but I couldn’t generate a response just now. Please try again."
    except urllib.error.URLError:
        return (
            "I’m not able to reach my language model right now. "
            "Please make sure Ollama is running, then try again."
        )
    except Exception as e:
        return f"I hit a response error: {e}"