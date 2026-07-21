from __future__ import annotations

import time
from typing import Any

from app.analytics.agent_metrics import agent_metrics_tracker


class OrchestratorService:
    def __init__(self) -> None:
        self.agent_keywords: dict[str, list[str]] = {
            "hr_agent": [
                "leave",
                "salary",
                "employee",
                "policy",
                "holiday",
                "payroll",
            ],
            "project_agent": [
                "project",
                "sprint",
                "task",
                "roadmap",
                "deadline",
                "risk",
            ],
            "document_agent": [
                "document",
                "file",
                "knowledge",
                "search",
                "pdf",
            ],
        }

    def select_agent(self, query: str) -> str:
        normalized_query = query.lower()

        best_agent = "general_agent"
        best_score = 0

        for agent_name, keywords in self.agent_keywords.items():
            score = sum(
                1
                for keyword in keywords
                if keyword in normalized_query
            )

            if score > best_score:
                best_score = score
                best_agent = agent_name

        return best_agent

    def select_tools(
        self,
        agent_name: str,
    ) -> list[str]:
        tools_by_agent = {
            "hr_agent": [
                "document_search",
                "employee_directory",
            ],
            "project_agent": [
                "project_tracker",
                "workflow_manager",
            ],
            "document_agent": [
                "document_search",
            ],
            "general_agent": [],
        }

        return tools_by_agent.get(
            agent_name,
            [],
        )

    async def execute(
        self,
        query: str,
        user_id: str | None = None,
    ) -> dict[str, Any]:
        start_time = time.perf_counter()

        selected_agent = self.select_agent(query)
        selected_tools = self.select_tools(
            selected_agent,
        )

        try:
            result = await self._run_agent(
                agent_name=selected_agent,
                query=query,
                tools=selected_tools,
            )

            duration_ms = (
                time.perf_counter() - start_time
            ) * 1000

            agent_metrics_tracker.record_execution(
                agent_name=selected_agent,
                status="success",
                response_time_ms=duration_ms,
                input_tokens=max(
                    len(query.split()),
                    1,
                ),
                output_tokens=max(
                    len(result.split()),
                    1,
                ),
                tool_names=selected_tools,
                workflow_id=None,
                workflow_duration_ms=None,
                error_message=None,
            )

            return {
                "status": "success",
                "agent": selected_agent,
                "tools": selected_tools,
                "query": query,
                "answer": result,
                "duration_ms": round(
                    duration_ms,
                    2,
                ),
                "user_id": user_id,
            }

        except Exception as exc:
            duration_ms = (
                time.perf_counter() - start_time
            ) * 1000

            agent_metrics_tracker.record_execution(
                agent_name=selected_agent,
                status="failed",
                response_time_ms=duration_ms,
                input_tokens=max(
                    len(query.split()),
                    1,
                ),
                output_tokens=0,
                tool_names=selected_tools,
                workflow_id=None,
                workflow_duration_ms=None,
                error_message=str(exc),
            )

            raise

    async def _run_agent(
        self,
        agent_name: str,
        query: str,
        tools: list[str],
    ) -> str:
        tool_text = (
            ", ".join(tools)
            if tools
            else "no external tools"
        )

        return (
            f"The {agent_name} handled your request: "
            f"'{query}'. Selected tools: {tool_text}."
        )


orchestrator_service = OrchestratorService()