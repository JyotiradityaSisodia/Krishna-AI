from abc import ABC, abstractmethod


class BrainAdapter(ABC):
    @abstractmethod
    def generate_reply(self, user_input: str, system_prompt: str = "") -> str:
        pass