import requests
from brain.base import BrainAdapter

LLAMA_SERVER_URL = "http://127.0.0.1:8080/completion"


class LlamaCppAdapter(BrainAdapter):
    def generate_reply(self, user_input: str, system_prompt: str = "") -> str:
        prompt = f"{system_prompt}\nUser: {user_input}\nKrishna:"

        try:
            res = requests.post(
                LLAMA_SERVER_URL,
                json={
                    "prompt": prompt,
                    "n_predict": 80,
                    "temperature": 0.6,
                    "stop": ["User:", "\nUser:", "\nKrishna:"]
                },
                timeout=30
            )

            if not res.ok:
                return f"Krishna error: local brain server returned {res.status_code}: {res.text}"

            data = res.json()
            reply = data.get("content", "").strip()

            if not reply:
                return "Krishna could not generate a reply."

            return reply

        except requests.exceptions.Timeout:
            return "Krishna error: local brain server timed out."
        except Exception as e:
            return f"Krishna error: {str(e)}"