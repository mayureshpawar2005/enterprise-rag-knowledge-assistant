"""In-memory chat history per session (bonus feature)."""

import uuid
from collections import defaultdict
from datetime import datetime, timezone
from threading import Lock
from typing import Dict, List, Optional

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from app.config import Settings, get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ChatHistoryService:
    """Thread-safe in-memory store for multi-turn conversations."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._sessions: Dict[str, List[dict]] = defaultdict(list)
        self._lock = Lock()

    def get_or_create_session(self, session_id: Optional[str]) -> str:
        """Return existing session ID or create a new one."""
        if session_id:
            return session_id
        new_id = str(uuid.uuid4())
        logger.info("Created new chat session: %s", new_id)
        return new_id

    def get_langchain_messages(self, session_id: str) -> List[BaseMessage]:
        """Convert stored history to LangChain messages for the LLM."""
        with self._lock:
            records = self._sessions.get(session_id, [])

        messages: List[BaseMessage] = []
        for record in records[-self._settings.max_chat_history_messages :]:
            if record["role"] == "user":
                messages.append(HumanMessage(content=record["content"]))
            elif record["role"] == "assistant":
                messages.append(AIMessage(content=record["content"]))
        return messages

    def append_exchange(
        self,
        session_id: str,
        question: str,
        answer: str,
    ) -> None:
        """Store user question and assistant answer."""
        now = datetime.now(timezone.utc).isoformat()
        with self._lock:
            self._sessions[session_id].append(
                {"role": "user", "content": question, "timestamp": now}
            )
            self._sessions[session_id].append(
                {"role": "assistant", "content": answer, "timestamp": now}
            )
            # Trim old messages
            max_records = self._settings.max_chat_history_messages * 2
            if len(self._sessions[session_id]) > max_records:
                self._sessions[session_id] = self._sessions[session_id][-max_records:]

        logger.debug("Updated chat history for session %s", session_id)

    def get_history(self, session_id: str) -> List[dict]:
        """Return raw history for a session."""
        with self._lock:
            return list(self._sessions.get(session_id, []))
