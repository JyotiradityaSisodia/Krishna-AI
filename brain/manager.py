from app.config import BRAIN_BACKEND
from brain.llamacpp_adapter import LlamaCppAdapter
from brain.mock_adapter import MockAdapter


def get_brain():
    if BRAIN_BACKEND == "mock":
        return MockAdapter()

    if BRAIN_BACKEND == "llamacpp":
        return LlamaCppAdapter()

    return LlamaCppAdapter()