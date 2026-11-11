from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str


class MemoryRequest(BaseModel):
    mem_type: str
    key: str
    value: str