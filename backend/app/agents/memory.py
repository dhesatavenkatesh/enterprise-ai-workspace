from __future__ import annotations

from collections import defaultdict, deque
from threading import RLock


class AgentMemory:
    def __init__(self, max_messages: int = 20) -> None:
        self.max_messages = max_messages
        self._messages: dict[str, deque[dict[str, str]]] = defaultdict(
            lambda: deque(maxlen=self.max_messages)
        )
        self._lock = RLock()

    def add(self, conversation_id: str, role: str, content: str) -> None:
        if not conversation_id or not content:
            return
        with self._lock:
            self._messages[conversation_id].append({"role": role, "content": content})

    def get(self, conversation_id: str | None) -> list[dict[str, str]]:
        if not conversation_id:
            return []
        with self._lock:
            return list(self._messages.get(conversation_id, ()))

    def clear(self, conversation_id: str) -> None:
        with self._lock:
            self._messages.pop(conversation_id, None)


agent_memory = AgentMemory()
