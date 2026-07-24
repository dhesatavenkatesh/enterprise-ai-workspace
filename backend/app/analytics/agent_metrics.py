from __future__ import annotations

import json
import threading
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from uuid import uuid4

BASE_DIR = Path(__file__).resolve().parents[2]

METRICS_DIRECTORY = BASE_DIR / "storage"
METRICS_FILE = METRICS_DIRECTORY / "agent_metrics.json"


@dataclass
class AgentExecutionMetric:
    id: str
    agent_name: str
    status: str
    response_time_ms: float
    input_tokens: int
    output_tokens: int
    tool_names: list[str]
    workflow_id: str | None
    workflow_duration_ms: float | None
    error_message: str | None
    created_at: str

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens


class AgentMetricsTracker:
    """
    Thread-safe agent analytics tracker.

    Metrics are persisted to:
        backend/storage/agent_metrics.json
    """

    def __init__(
        self,
        metrics_file: Path = METRICS_FILE,
    ) -> None:
        self.metrics_file = metrics_file
        self._lock = threading.RLock()

        self.metrics_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        if not self.metrics_file.exists():
            self._write_metrics([])

    def _read_metrics(self) -> list[dict[str, Any]]:
        with self._lock:
            try:
                with self.metrics_file.open(
                    "r",
                    encoding="utf-8",
                ) as file:
                    data = json.load(file)

                if not isinstance(data, list):
                    return []

                return data
            except (
                FileNotFoundError,
                json.JSONDecodeError,
                OSError,
            ):
                return []

    def _write_metrics(
        self,
        metrics: list[dict[str, Any]],
    ) -> None:
        with self._lock:
            temporary_file = self.metrics_file.with_suffix(".tmp")

            with temporary_file.open(
                "w",
                encoding="utf-8",
            ) as file:
                json.dump(
                    metrics,
                    file,
                    indent=2,
                    ensure_ascii=False,
                )

            temporary_file.replace(
                self.metrics_file,
            )

    def record_execution(
        self,
        *,
        agent_name: str,
        status: str,
        response_time_ms: float,
        input_tokens: int = 0,
        output_tokens: int = 0,
        tool_names: list[str] | None = None,
        workflow_id: str | None = None,
        workflow_duration_ms: float | None = None,
        error_message: str | None = None,
    ) -> AgentExecutionMetric:
        normalized_status = status.strip().lower()

        if normalized_status not in {
            "success",
            "failed",
        }:
            raise ValueError(
                "status must be 'success' or 'failed'",
            )

        metric = AgentExecutionMetric(
            id=str(uuid4()),
            agent_name=agent_name.strip() or "unknown_agent",
            status=normalized_status,
            response_time_ms=max(
                float(response_time_ms),
                0.0,
            ),
            input_tokens=max(int(input_tokens), 0),
            output_tokens=max(int(output_tokens), 0),
            tool_names=[tool.strip() for tool in (tool_names or []) if tool.strip()],
            workflow_id=workflow_id,
            workflow_duration_ms=(
                max(float(workflow_duration_ms), 0.0) if workflow_duration_ms is not None else None
            ),
            error_message=error_message,
            created_at=datetime.now(
                UTC,
            ).isoformat(),
        )

        with self._lock:
            metrics = self._read_metrics()
            metrics.append(asdict(metric))
            self._write_metrics(metrics)

        return metric

    def list_executions(
        self,
        *,
        agent_name: str | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        metrics = self._read_metrics()

        if agent_name:
            normalized_name = agent_name.lower()

            metrics = [
                metric
                for metric in metrics
                if str(
                    metric.get("agent_name", ""),
                ).lower()
                == normalized_name
            ]

        if status:
            normalized_status = status.lower()

            metrics = [
                metric
                for metric in metrics
                if str(
                    metric.get("status", ""),
                ).lower()
                == normalized_status
            ]

        metrics.sort(
            key=lambda item: str(
                item.get("created_at", ""),
            ),
            reverse=True,
        )

        return metrics[: max(1, min(limit, 500))]

    def get_summary(self) -> dict[str, Any]:
        metrics = self._read_metrics()

        total_executions = len(metrics)

        successful_runs = sum(1 for metric in metrics if metric.get("status") == "success")

        failed_runs = sum(1 for metric in metrics if metric.get("status") == "failed")

        response_times = [
            float(
                metric.get(
                    "response_time_ms",
                    0,
                ),
            )
            for metric in metrics
        ]

        average_response_time_ms = (
            sum(response_times) / len(response_times) if response_times else 0.0
        )

        total_input_tokens = sum(int(metric.get("input_tokens", 0)) for metric in metrics)

        total_output_tokens = sum(int(metric.get("output_tokens", 0)) for metric in metrics)

        workflow_durations = [
            float(metric["workflow_duration_ms"])
            for metric in metrics
            if metric.get(
                "workflow_duration_ms",
            )
            is not None
        ]

        average_workflow_duration_ms = (
            sum(workflow_durations) / len(workflow_durations) if workflow_durations else 0.0
        )

        success_rate = successful_runs / total_executions * 100 if total_executions else 0.0

        return {
            "total_executions": total_executions,
            "successful_runs": successful_runs,
            "failed_runs": failed_runs,
            "success_rate": round(
                success_rate,
                2,
            ),
            "average_response_time_ms": round(
                average_response_time_ms,
                2,
            ),
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": (total_input_tokens + total_output_tokens),
            "average_workflow_duration_ms": round(
                average_workflow_duration_ms,
                2,
            ),
        }

    def get_agent_leaderboard(
        self,
    ) -> list[dict[str, Any]]:
        metrics = self._read_metrics()

        grouped: dict[
            str,
            list[dict[str, Any]],
        ] = defaultdict(list)

        for metric in metrics:
            agent_name = str(
                metric.get(
                    "agent_name",
                    "unknown_agent",
                ),
            )

            grouped[agent_name].append(metric)

        leaderboard: list[dict[str, Any]] = []

        for agent_name, executions in grouped.items():
            total = len(executions)

            successful = sum(1 for execution in executions if execution.get("status") == "success")

            failed = total - successful

            average_response_time = (
                sum(
                    float(
                        execution.get(
                            "response_time_ms",
                            0,
                        ),
                    )
                    for execution in executions
                )
                / total
                if total
                else 0.0
            )

            token_usage = sum(
                int(
                    execution.get(
                        "input_tokens",
                        0,
                    ),
                )
                + int(
                    execution.get(
                        "output_tokens",
                        0,
                    ),
                )
                for execution in executions
            )

            success_rate = successful / total * 100 if total else 0.0

            leaderboard.append(
                {
                    "agent_name": agent_name,
                    "total_executions": total,
                    "successful_runs": successful,
                    "failed_runs": failed,
                    "success_rate": round(
                        success_rate,
                        2,
                    ),
                    "average_response_time_ms": round(
                        average_response_time,
                        2,
                    ),
                    "token_usage": token_usage,
                },
            )

        leaderboard.sort(
            key=lambda item: (
                item["success_rate"],
                item["total_executions"],
            ),
            reverse=True,
        )

        for index, item in enumerate(
            leaderboard,
            start=1,
        ):
            item["rank"] = index

        return leaderboard

    def get_tool_usage(
        self,
    ) -> list[dict[str, Any]]:
        metrics = self._read_metrics()

        tool_counter: Counter[str] = Counter()

        for metric in metrics:
            for tool_name in metric.get(
                "tool_names",
                [],
            ):
                tool_counter[str(tool_name)] += 1

        return [
            {
                "tool_name": tool_name,
                "usage_count": usage_count,
            }
            for tool_name, usage_count in tool_counter.most_common()
        ]

    def get_trends(
        self,
        days: int = 7,
    ) -> list[dict[str, Any]]:
        safe_days = max(1, min(days, 90))

        metrics = self._read_metrics()

        now = datetime.now(UTC)
        start_date = (now - timedelta(days=safe_days - 1)).date()

        daily_data: dict[
            str,
            dict[str, Any],
        ] = {}

        for day_offset in range(safe_days):
            current_date = start_date + timedelta(days=day_offset)

            date_key = current_date.isoformat()

            daily_data[date_key] = {
                "date": date_key,
                "total_executions": 0,
                "successful_runs": 0,
                "failed_runs": 0,
                "token_usage": 0,
                "average_response_time_ms": 0.0,
                "_response_times": [],
            }

        for metric in metrics:
            created_at_value = metric.get(
                "created_at",
            )

            if not created_at_value:
                continue

            try:
                created_at = datetime.fromisoformat(
                    str(created_at_value),
                )

                metric_date = created_at.date().isoformat()
            except ValueError:
                continue

            if metric_date not in daily_data:
                continue

            day = daily_data[metric_date]

            day["total_executions"] += 1

            if metric.get("status") == "success":
                day["successful_runs"] += 1
            else:
                day["failed_runs"] += 1

            day["token_usage"] += int(metric.get("input_tokens", 0)) + int(
                metric.get("output_tokens", 0)
            )

            day["_response_times"].append(
                float(
                    metric.get(
                        "response_time_ms",
                        0,
                    ),
                ),
            )

        result: list[dict[str, Any]] = []

        for date_key in sorted(daily_data):
            day = daily_data[date_key]

            response_times = day.pop(
                "_response_times",
            )

            day["average_response_time_ms"] = round(
                (sum(response_times) / len(response_times)) if response_times else 0.0,
                2,
            )

            result.append(day)

        return result

    def get_dashboard(
        self,
        days: int = 7,
    ) -> dict[str, Any]:
        return {
            "summary": self.get_summary(),
            "leaderboard": (self.get_agent_leaderboard()),
            "tool_usage": self.get_tool_usage(),
            "trends": self.get_trends(days),
            "recent_executions": (self.list_executions(limit=10)),
        }


agent_metrics_tracker = AgentMetricsTracker()
