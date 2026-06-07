import os
from datetime import datetime, timezone
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


class SupabaseLogger:
    def __init__(self):
        self._client: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY"),
        )

    def create_session(self, telegram_chat_id: int, thread_id: str) -> str:
        """Creates a new session row. Returns the session UUID."""
        result = self._client.table("sessions").insert({
            "telegram_chat_id": telegram_chat_id,
            "thread_id": thread_id,
        }).execute()
        return result.data[0]["id"]

    def log_message(self, session_id: str, role: str, content: str, blocked: bool = False) -> str:
        """Logs a user or assistant message. Returns the message UUID."""
        result = self._client.table("messages").insert({
            "session_id": session_id,
            "role": role,
            "content": content,
            "blocked": blocked,
        }).execute()
        return result.data[0]["id"]

    def log_trace(
        self,
        session_id: str,
        message_id: str,
        step_order: int,
        node_name: str,
        started_at: datetime,
        ended_at: datetime,
        input: dict | None = None,
        output: dict | None = None,
        tool_name: str | None = None,
    ) -> None:
        """Logs a single LangGraph node execution with timing and step order."""
        duration_ms = int((ended_at - started_at).total_seconds() * 1000)
        self._client.table("traces").insert({
            "session_id": session_id,
            "message_id": message_id,
            "step_order": step_order,
            "node_name": node_name,
            "tool_name": tool_name,
            "started_at": started_at.isoformat(),
            "ended_at": ended_at.isoformat(),
            "duration_ms": duration_ms,
            "input": input,
            "output": output,
        }).execute()

    @staticmethod
    def now() -> datetime:
        return datetime.now(timezone.utc)
