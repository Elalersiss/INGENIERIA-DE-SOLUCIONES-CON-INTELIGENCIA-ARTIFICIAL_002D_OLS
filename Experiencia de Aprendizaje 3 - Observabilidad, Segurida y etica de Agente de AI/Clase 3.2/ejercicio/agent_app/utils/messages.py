from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from agent_app.models import Message


def to_lc_message(m: Message):
    if m.role == "assistant":
        return AIMessage(content=m.content)
    if m.role == "system":
        return SystemMessage(content=m.content)
    return HumanMessage(content=m.content)
