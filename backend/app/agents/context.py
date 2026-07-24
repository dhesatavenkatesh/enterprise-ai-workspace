from __future__ import annotations

from app.agents.schemas import AgentRequest


class AgentContextManager:
    @staticmethod
    def build(request: AgentRequest, memory: list[dict[str, str]] | None = None) -> str:
        parts: list[str] = []
        if request.context:
            parts.append(f"Additional context: {request.context}")
        if request.metadata:
            parts.append(f"Request metadata: {request.metadata}")
        if memory:
            history = "\n".join(
                f"{item.get('role', 'user')}: {item.get('content', '')}" for item in memory
            )
            parts.append(f"Recent conversation memory:\n{history}")
        return "\n\n".join(parts)
