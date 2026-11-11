from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseSkill(ABC):
    name = "base_skill"
    required_fields = []

    @abstractmethod
    def run(self, params: Dict[str, Any], session: Dict[str, Any]) -> Dict[str, Any]:
        pass

    @abstractmethod
    def execute(self, params: Dict[str, Any], session: Dict[str, Any]) -> Dict[str, Any]:
        pass

    def get_missing_fields(self, params: Dict[str, Any]) -> list:
        missing = []
        for field in self.required_fields:
            if not params.get(field):
                missing.append(field)
        return missing