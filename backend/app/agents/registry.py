from __future__ import annotations

from threading import RLock

from app.agents.base_agent import BaseAgent


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}
        self._lock = RLock()

    def register(self, agent: BaseAgent, *, replace: bool = False) -> BaseAgent:
        with self._lock:
            if agent.name in self._agents and not replace:
                return self._agents[agent.name]
            self._agents[agent.name] = agent
            return agent

    def get(self, name: str) -> BaseAgent:
        try:
            return self._agents[name]
        except KeyError as exc:
            raise KeyError(f"Agent '{name}' is not registered.") from exc

    def list(self) -> list[dict]:
        return [agent.definition().model_dump() for agent in self._agents.values()]

    def all(self) -> list[BaseAgent]:
        return list(self._agents.values())

    def clear(self) -> None:
        with self._lock:
            self._agents.clear()


agent_registry = AgentRegistry()
