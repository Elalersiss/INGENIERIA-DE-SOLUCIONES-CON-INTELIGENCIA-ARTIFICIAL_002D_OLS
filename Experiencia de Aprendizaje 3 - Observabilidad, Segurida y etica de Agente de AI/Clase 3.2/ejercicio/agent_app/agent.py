from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, AIMessage
from langchain_core.runnables import RunnableConfig
from typing import TypedDict, Annotated
from datetime import date
from dotenv import load_dotenv

from agent_app.tools import rag_search
from agent_app.prompts import AGENT_SYSTEM_PROMPT, QUERY_REFORMULATION_PROMPT


load_dotenv()

MODEL = "gpt-4o-mini"

tools = [rag_search]


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


def _get_llm(model: str):
    return ChatOpenAI(model=model, temperature=0).bind_tools(tools)


def _get_query_llm(model: str):
    return ChatOpenAI(model=model, temperature=0)


def call_model(state: AgentState, config: RunnableConfig) -> AgentState:
    model = config.get("configurable", {}).get("model", MODEL)
    today = date.today().strftime("%Y-%m-%d")
    system = SystemMessage(content=AGENT_SYSTEM_PROMPT + f"\n\nFecha de hoy: {today}")
    response = _get_llm(model).invoke([system] + state["messages"])
    return {"messages": [response]}


def generate_query(state: AgentState, config: RunnableConfig) -> AgentState:
    """Reformulates the conversation history into an optimized search query."""
    model = config.get("configurable", {}).get("model", MODEL)
    conversation = "\n".join(
        f"{m.type}: {m.content}" for m in state["messages"] if m.content
    )
    prompt = [
        SystemMessage(content=QUERY_REFORMULATION_PROMPT),
        SystemMessage(content=f"Conversation:\n{conversation}"),
    ]
    result = _get_query_llm(model).invoke(prompt)
    search_query = result.content.strip()

    last_message = state["messages"][-1]
    updated_tool_calls = [
        {**tc, "args": {"query": search_query}}
        for tc in last_message.tool_calls
    ]
    updated_message = AIMessage(
        id=last_message.id,
        content=last_message.content,
        tool_calls=updated_tool_calls,
    )
    return {"messages": [updated_message]}


def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "generate_query"
    return END


tool_node = ToolNode(tools)

graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_node("generate_query", generate_query)
graph.add_node("tools", tool_node)

graph.set_entry_point("agent")
graph.add_conditional_edges("agent", should_continue, {
    "generate_query": "generate_query",
    END: END,
})
graph.add_edge("generate_query", "tools")
graph.add_edge("tools", "agent")

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)