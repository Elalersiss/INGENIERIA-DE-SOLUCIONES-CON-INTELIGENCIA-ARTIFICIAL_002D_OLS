from pydantic import BaseModel


class Message(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str


class ChatRequest(BaseModel):
    model: str
    conversation: list[Message]
    question: str


class ChatResponse(BaseModel):
    answer: str
    prompt_tokens: int
    completion_tokens: int
