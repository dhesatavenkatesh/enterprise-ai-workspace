from __future__ import annotations

from app.agents.executor import AgentExecutor
from app.agents.registry import AgentRegistry, agent_registry
from app.agents.schemas import AgentRequest, AgentStatus
from app.orchestrator.aggregator import ResultAggregator
from app.orchestrator.router import AgentRouter
from app.orchestrator.schemas import (
    OrchestrationMode,
    OrchestratorRequest,
    OrchestratorResponse,
    RoutingDecision,
)


class AgentOrchestrator:
    def __init__(
        self,
        registry: AgentRegistry | None = None,
        executor: AgentExecutor | None = None,
        router: AgentRouter | None = None,
    ) -> None:
        self.registry = registry or agent_registry
        self.executor = executor or AgentExecutor()
        self.router = router or AgentRouter(self.registry)
        self.aggregator = ResultAggregator()

    def _validate_agents(self, names: list[str]) -> None:
        available = {agent.name for agent in self.registry.all()}
        unknown = [name for name in names if name not in available]
        if unknown:
            raise ValueError(
                f"Unknown agent(s): {', '.join(unknown)}. "
                f"Available agents: {', '.join(sorted(available))}."
            )

    @staticmethod
    def _build_agent_request(payload: OrchestratorRequest, user_id: int | str | None) -> AgentRequest:
        return AgentRequest(
            message=payload.message,
            user_id=user_id,
            conversation_id=payload.conversation_id,
            context=payload.context,
            metadata=payload.metadata,
        )

    async def auto_route(self, payload: OrchestratorRequest, *, user_id: int | str | None = None) -> OrchestratorResponse:
        route = self.router.route(payload.message, max_agents=1)
        request = self._build_agent_request(payload, user_id)
        results = [await self.executor.execute(request, route.agent_names[0])]
        return self._response(OrchestrationMode.AUTO, route.agent_names, route.reason, route.confidence, results)

    async def execute_single(self, payload: OrchestratorRequest, *, user_id: int | str | None = None) -> OrchestratorResponse:
        if not payload.agent_name:
            raise ValueError("agent_name is required for single-agent execution.")
        self._validate_agents([payload.agent_name])
        request = self._build_agent_request(payload, user_id)
        results = [await self.executor.execute(request, payload.agent_name)]
        return self._response(
            OrchestrationMode.SINGLE,
            [payload.agent_name],
            "Agent explicitly selected by the caller.",
            1.0,
            results,
        )

    async def execute_multi(self, payload: OrchestratorRequest, *, user_id: int | str | None = None) -> OrchestratorResponse:
        names = payload.agent_names
        if not names:
            route = self.router.route(payload.message, max_agents=3)
            names = route.agent_names
            reason = route.reason
            confidence = route.confidence
        else:
            self._validate_agents(names)
            reason = "Agents explicitly selected by the caller."
            confidence = 1.0

        request = self._build_agent_request(payload, user_id)
        results = await self.executor.execute_parallel(request, names)
        return self._response(OrchestrationMode.MULTI, names, reason, confidence, results)

    def _response(self, mode, names, reason, confidence, results) -> OrchestratorResponse:
        successful = sum(result.status == AgentStatus.SUCCESS for result in results)
        failed = len(results) - successful
        return OrchestratorResponse(
            mode=mode,
            routing=RoutingDecision(
                selected_agents=names,
                reason=reason,
                confidence=confidence,
            ),
            results=results,
            final_answer=self.aggregator.aggregate(results),
            successful_agents=successful,
            failed_agents=failed,
        )
