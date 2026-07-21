from __future__ import annotations

from app.workflows.schemas import WorkflowCreate, WorkflowDefinition
from app.workflows.store import WorkflowStore, workflow_store


class WorkflowService:
    def __init__(self, store: WorkflowStore | None = None) -> None:
        self.store = store or workflow_store

    def create(self, payload: WorkflowCreate, owner_id: int | str | None) -> WorkflowDefinition:
        workflow = WorkflowDefinition(**payload.model_dump(), owner_id=owner_id)
        return self.store.create(workflow)

    def list(self, owner_id: int | str | None) -> list[WorkflowDefinition]:
        return self.store.list(owner_id)

    def get(self, workflow_id: str, owner_id: int | str | None) -> WorkflowDefinition:
        workflow = self.store.get(workflow_id)
        if owner_id is not None and str(workflow.owner_id) != str(owner_id):
            raise PermissionError("You do not have access to this workflow.")
        return workflow
