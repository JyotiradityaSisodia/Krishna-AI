from brain.base import BrainAdapter


class MockAdapter(BrainAdapter):
    def generate_reply(self, user_input: str, system_prompt: str = "") -> str:
        return f"[MOCK BRAIN] Krishna heard: {user_input}"