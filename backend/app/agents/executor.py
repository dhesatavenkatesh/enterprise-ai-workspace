from __future__ import annotations

import asyncio

from app.agents.factory import AgentFactory
from app.agents.schemas import AgentRequest, AgentResponse, AgentStatus


class AgentExecutor:
    def __init__(
        self,
        factory: AgentFactory | None = None,
        timeout_seconds: float = 60.0,
        max_retries: int = 2,
    ) -> None:
        self.factory = factory or AgentFactory()
        self.timeout_seconds = timeout_seconds
        self.max_retries = max(1, max_retries)

    async def execute(
        self,
        request: AgentRequest,
        agent_name: str | None = None,
    ) -> AgentResponse:
        agent = (
            self.factory.create(agent_name) if agent_name else self.factory.select(request.message)
        )
        last_error: Exception | None = None
        for attempt in range(1, self.max_retries + 1):
            try:
                return await asyncio.wait_for(agent.execute(request), timeout=self.timeout_seconds)
            except TimeoutError:
                last_error = TimeoutError(
                    f"Agent '{agent.name}' timed out after {self.timeout_seconds} seconds."
                )
            except Exception as exc:  # executor boundary
                last_error = exc
            if attempt < self.max_retries:
                await asyncio.sleep(min(attempt, 2))

        status = AgentStatus.TIMEOUT if isinstance(last_error, TimeoutError) else AgentStatus.FAILED
        return AgentResponse(
            agent_name=agent.name,
            status=status,
            error=str(last_error) if last_error else "Unknown agent execution error.",
        )

    async def execute_parallel(
        self,
        request: AgentRequest,
        agent_names: list[str],
    ) -> list[AgentResponse]:
        return await asyncio.gather(*(self.execute(request, name) for name in agent_names))
