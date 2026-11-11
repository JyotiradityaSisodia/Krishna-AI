import requests
from brain.base import BrainAdapter
from app.config import OLLAMA_URL, MODEL_NAME, BACKEND_TIMEOUT


class OllamaAdapter(BrainAdapter):
    def generate_reply(self, user_input: str, system_prompt: str = "") -> str:
        messages = []

        if system_prompt.strip():
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": user_input})

        try:
            res = requests.post(
                OLLAMA_URL,
                json={
                    "model": MODEL_NAME,
                    "messages": messages,
                    "stream": False
                },
                timeout=BACKEND_TIMEOUT
            )

            if not res.ok:
                return f"Krishna error: Ollama returned {res.status_code}: {res.text}"

            data = res.json()
            return data.get("message", {}).get("content", "No reply received.")

        except requests.exceptions.Timeout:
            return "Krishna error: backend timed out waiting for Ollama."
        except Exception as e:
            return f"Krishna error: {str(e)}"