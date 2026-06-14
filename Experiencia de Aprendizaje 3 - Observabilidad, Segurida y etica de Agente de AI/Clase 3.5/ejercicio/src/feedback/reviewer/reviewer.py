import os
from typing import Annotated, TypedDict
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from dotenv import load_dotenv

from src.feedback.prompts import REVIEWER_SYSTEM_PROMPT
from src.feedback.reviewer.reviewer_tools import get_bad_conversations, list_repo_files, read_repo_file, save_suggestion

load_dotenv()

TOOLS = [get_bad_conversations, list_repo_files, read_repo_file, save_suggestion]

INITIAL_MESSAGE = (
    "Fetch all bad conversations using get_bad_conversations. "
    "Then for each one, read the relevant source file from the repository and suggest a specific improvement. "
    "Process each conversation separately — do not mix issues from different sessions."
)


class ReviewerState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


class ConversationReviewerAgent:
    def __init__(self, model: str = "gpt-4o"):
        self._model = model
        self._graph = self._build_graph()

    def run(self) -> str:
        """
        Fetches all bad conversations, reads the relevant repo files,
        and returns a report with suggestions per conversation.
        """
        result = self._graph.invoke({
            "messages": [HumanMessage(content=INITIAL_MESSAGE)]
        })
        suggestions = result["messages"][-1].content
        print(suggestions)
        return suggestions

    def _build_graph(self):
        llm = ChatOpenAI(model=self._model, temperature=0).bind_tools(TOOLS)
        tool_node = ToolNode(TOOLS)

        def agent_node(state: ReviewerState):
            messages = [SystemMessage(content=REVIEWER_SYSTEM_PROMPT)] + state["messages"]
            response = llm.invoke(messages)
            return {"messages": [response]}

        def should_continue(state: ReviewerState):
            last = state["messages"][-1]
            if hasattr(last, "tool_calls") and last.tool_calls:
                return "tools"
            return END

        graph = StateGraph(ReviewerState)
        graph.add_node("agent", agent_node)
        graph.add_node("tools", tool_node)
        graph.set_entry_point("agent")
        graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
        graph.add_edge("tools", "agent")
        return graph.compile()


if __name__ == "__main__":
    agent = ConversationReviewerAgent(model="gpt-4o")
    agent.run()