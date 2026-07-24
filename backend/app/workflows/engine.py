from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from app.agents.bootstrap import register_default_agents
from app.approvals.schemas import ApprovalCreate, ApprovalStatus
from app.approvals.service import ApprovalService
from app.mcp.bootstrap import register_default_tools
from app.mcp.executor import MCPExecutor
from app.orchestrator.schemas import OrchestratorRequest
from app.orchestrator.service import AgentOrchestrator
from app.workflows.schemas import (
    WorkflowDefinition,
    WorkflowRunRequest,
    WorkflowRunResult,
    WorkflowRunStatus,
    WorkflowStepResult,
    WorkflowStepType,
)
from app.workflows.store import WorkflowStore, workflow_store


def utc_now() -> datetime:
    return datetime.now(UTC)


class WorkflowEngine:
    def __init__(self, store: WorkflowStore | None = None) -> None:
        self.store = store or workflow_store
        self.orchestrator = AgentOrchestrator(registry=register_default_agents())
        self.mcp_executor = MCPExecutor(registry=register_default_tools())
        self.approvals = ApprovalService()

    async def run(
        self,
        workflow: WorkflowDefinition,
        request: WorkflowRunRequest,
        *,
        user_id: int | str | None = None,
    ) -> WorkflowRunResult:
        run = WorkflowRunResult(
            workflow_id=workflow.id,
            workflow_name=workflow.name,
            status=WorkflowRunStatus.RUNNING,
            initial_input=request.input,
            context=request.context,
            conversation_id=request.conversation_id,
        )
        self.store.save_run(run)
        return await self._execute(workflow, run, user_id=user_id)

    async def resume(
        self,
        workflow: WorkflowDefinition,
        run: WorkflowRunResult,
        *,
        user_id: int | str | None = None,
    ) -> WorkflowRunResult:
        if run.status != WorkflowRunStatus.WAITING_APPROVAL:
            raise ValueError("This workflow run is not waiting for approval.")
        if not run.pending_approval_id:
            raise ValueError("The workflow run has no pending approval request.")

        approval = self.approvals.get(run.pending_approval_id)
        if approval.status == ApprovalStatus.PENDING:
            raise ValueError("The approval request is still pending.")
        if approval.status == ApprovalStatus.REJECTED:
            run.status = WorkflowRunStatus.REJECTED
            run.error = approval.decision_comment or "Workflow step was rejected."
            run.completed_at = utc_now()
            self.store.save_run(run)
            return run
        if approval.status != ApprovalStatus.APPROVED:
            raise ValueError(f"Approval status '{approval.status.value}' cannot resume a workflow.")

        run.status = WorkflowRunStatus.RUNNING
        run.pending_approval_id = None
        return await self._execute(
            workflow,
            run,
            user_id=user_id,
            approval_already_granted=True,
        )

    async def _execute(
        self,
        workflow: WorkflowDefinition,
        run: WorkflowRunResult,
        *,
        user_id: int | str | None,
        approval_already_granted: bool = False,
    ) -> WorkflowRunResult:
        current_output: Any = (
            run.step_results[-1].output
            if run.step_results and run.step_results[-1].success
            else run.initial_input
        )

        try:
            for index in range(run.current_step_index, len(workflow.steps)):
                step = workflow.steps[index]
                run.current_step_index = index

                if step.requires_approval and not approval_already_granted:
                    approval = self.approvals.create(
                        ApprovalCreate(
                            title=f"Approve workflow step: {step.name}",
                            description=(
                                step.approval_reason
                                or f"Approval is required before executing '{step.target}'."
                            ),
                            resource_type="workflow_step",
                            resource_id=step.id,
                            requested_by=user_id,
                            payload={
                                "workflow_id": workflow.id,
                                "workflow_run_id": run.id,
                                "step_index": index,
                                "step_name": step.name,
                                "step_type": step.type.value,
                                "target": step.target,
                            },
                        )
                    )
                    run.status = WorkflowRunStatus.WAITING_APPROVAL
                    run.pending_approval_id = approval.id
                    self.store.save_run(run)
                    return run

                approval_already_granted = False
                started_at = utc_now()
                rendered_input = self._render(
                    step.input_template,
                    run.initial_input,
                    current_output,
                    run.context,
                )

                try:
                    if step.type == WorkflowStepType.AGENT:
                        response = await self.orchestrator.execute_single(
                            OrchestratorRequest(
                                message=rendered_input,
                                agent_name=step.target,
                                conversation_id=run.conversation_id,
                                context=run.context,
                                metadata={"workflow_id": workflow.id, "step_id": step.id},
                            ),
                            user_id=user_id,
                        )
                        current_output = response.final_answer
                    elif step.type == WorkflowStepType.MCP_TOOL:
                        arguments = dict(step.arguments)
                        arguments.setdefault("message", rendered_input)
                        result = await self.mcp_executor.execute(step.target, arguments)
                        if not result.success:
                            raise RuntimeError(result.error or "MCP tool execution failed.")
                        current_output = result.result
                    else:
                        raise ValueError(f"Unsupported workflow step type: {step.type}")

                    run.step_results.append(
                        WorkflowStepResult(
                            step_id=step.id,
                            step_name=step.name,
                            type=step.type,
                            target=step.target,
                            success=True,
                            output=current_output,
                            started_at=started_at,
                            completed_at=utc_now(),
                        )
                    )
                except Exception as exc:
                    run.step_results.append(
                        WorkflowStepResult(
                            step_id=step.id,
                            step_name=step.name,
                            type=step.type,
                            target=step.target,
                            success=False,
                            error=str(exc),
                            started_at=started_at,
                            completed_at=utc_now(),
                        )
                    )
                    if not step.continue_on_error:
                        raise

                run.current_step_index = index + 1
                self.store.save_run(run)

            run.status = WorkflowRunStatus.COMPLETED
            run.final_output = current_output
            run.completed_at = utc_now()
        except Exception as exc:
            run.status = WorkflowRunStatus.FAILED
            run.error = str(exc)
            run.completed_at = utc_now()

        self.store.save_run(run)
        return run

    @staticmethod
    def _render(
        template: str, initial_input: str, previous_output: Any, context: dict[str, Any]
    ) -> str:
        values = {
            "input": initial_input,
            "previous_output": str(previous_output),
            **{key: str(value) for key, value in context.items()},
        }
        try:
            return template.format_map(_SafeFormatDict(values))
        except Exception as exc:
            raise ValueError(f"Invalid workflow input template: {exc}") from exc


class _SafeFormatDict(dict):
    def __missing__(self, key: str) -> str:
        return "{" + key + "}"
