from __future__ import annotations

from threading import RLock

from app.workflows.schemas import WorkflowDefinition, WorkflowRunResult


class WorkflowStore:
    def __init__(self) -> None:
        self._workflows: dict[str, WorkflowDefinition] = {}
        self._runs: dict[str, WorkflowRunResult] = {}
        self._lock = RLock()

    def create(self, workflow: WorkflowDefinition) -> WorkflowDefinition:
        with self._lock:
            self._workflows[workflow.id] = workflow
        return workflow

    def list(self, owner_id: int | str | None = None) -> list[WorkflowDefinition]:
        with self._lock:
            values = list(self._workflows.values())
        if owner_id is None:
            return values
        return [item for item in values if str(item.owner_id) == str(owner_id)]

    def get(self, workflow_id: str) -> WorkflowDefinition:
        with self._lock:
            workflow = self._workflows.get(workflow_id)
        if workflow is None:
            raise KeyError(f"Workflow '{workflow_id}' was not found.")
        return workflow

    def save_run(self, run: WorkflowRunResult) -> WorkflowRunResult:
        with self._lock:
            self._runs[run.id] = run
        return run

    def get_run(self, run_id: str) -> WorkflowRunResult:
        with self._lock:
            run = self._runs.get(run_id)
        if run is None:
            raise KeyError(f"Workflow run '{run_id}' was not found.")
        return run

    def list_runs(self, workflow_id: str | None = None) -> list[WorkflowRunResult]:
        with self._lock:
            runs = list(self._runs.values())
        if workflow_id is None:
            return runs
        return [run for run in runs if run.workflow_id == workflow_id]


workflow_store = WorkflowStore()
