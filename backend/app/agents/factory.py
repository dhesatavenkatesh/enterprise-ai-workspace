from __future__ import annotations

import time

from app.agents.base_agent import BaseAgent
from app.agents.registry import AgentRegistry, agent_registry
from app.analytics.agent_metrics import (
    agent_metrics_tracker,
)


class AgentFactory:
    def __init__(self, registry: AgentRegistry | None = None) -> None:
        self.registry = registry or agent_registry

    def create(self, name: str) -> BaseAgent:
        return self.registry.get(name)

    def select(self, message: str) -> BaseAgent:
        for agent in self.registry.all():
            if agent.can_handle(message):
                return agent
        return self.registry.get("knowledge_agent")

    def execute_agent(
        agent,
        user_input: str,
        context: dict | None = None,
    ):
        started_at = time.perf_counter()

        try:
            result = agent.execute(
                user_input=user_input,
                context=context or {},
            )
            response_time_ms = (time.perf_counter() - started_at) * 1000

            result_data = result if isinstance(result, dict) else {}
            agent_metrics_tracker.record_execution(
                agent_name=getattr(
                    agent,
                    "name",
                    agent.__class__.__name__,
                ),
                status="success",
                response_time_ms=response_time_ms,
                input_tokens=int(
                    result_data.get(
                        "input_tokens",
                        0,
                    ),
                ),
                output_tokens=int(
                    result_data.get(
                        "output_tokens",
                        0,
                    ),
                ),
                tool_names=list(
                    result_data.get(
                        "tools_used",
                        [],
                    ),
                ),
            )
            return result

        except Exception as error:
            response_time_ms = (time.perf_counter() - started_at) * 1000

            agent_metrics_tracker.record_execution(
                agent_name=getattr(
                    agent,
                    "name",
                    agent.__class__.__name__,
                ),
                status="failed",
                response_time_ms=response_time_ms,
                error_message=str(error),
            )

        raise
