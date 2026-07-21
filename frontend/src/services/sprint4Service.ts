import axios, { type AxiosError } from "axios"

import api from "@/services/api"
import type {
  AgentExecutionRequest,
  AgentExecutionResponse,
  AgentListResponse,
  ApprovalListResponse,
  ApprovalRequest,
  ApprovalStatus,
  MCPDiscoveryResponse,
  MCPToolCallResponse,
  WorkflowCreate,
  WorkflowDefinition,
  WorkflowRunResult,
  Sprint4HealthResponse,
} from "@/types/sprint4"

function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{
      detail?: string
      message?: string
    }>

    return (
      axiosError.response?.data?.detail ??
      axiosError.response?.data?.message ??
      axiosError.message ??
      "Request failed"
    )
  }

  if (error instanceof Error) {
    return error.message
  }

  return "An unexpected error occurred"
}

async function execute<T>(
  request: () => Promise<{ data: T }>,
): Promise<T> {
  try {
    const response = await request()
    return response.data
  } catch (error) {
    throw new Error(getErrorMessage(error))
  }
}

export function getAgents(): Promise<AgentListResponse> {
  return execute(() =>
    api.get<AgentListResponse>("/api/agents"),
  )
}

export function executeAgent(
  payload: AgentExecutionRequest,
): Promise<AgentExecutionResponse> {
  return execute(() =>
    api.post<AgentExecutionResponse>(
      "/api/agents/execute",
      payload,
    ),
  )
}

export function executeMultipleAgents(
  payload: AgentExecutionRequest,
): Promise<AgentExecutionResponse> {
  return execute(() =>
    api.post<AgentExecutionResponse>(
      "/api/agents/execute-multi",
      payload,
    ),
  )
}

export function autoRouteAgent(
  payload: AgentExecutionRequest,
): Promise<AgentExecutionResponse> {
  return execute(() =>
    api.post<AgentExecutionResponse>(
      "/api/agents/route",
      payload,
    ),
  )
}

export function getMCPTools(): Promise<MCPDiscoveryResponse> {
  return execute(() =>
    api.get<MCPDiscoveryResponse>("/api/mcp/tools"),
  )
}

export function callMCPTool(
  toolName: string,
  args: Record<string, unknown>,
): Promise<MCPToolCallResponse> {
  return execute(() =>
    api.post<MCPToolCallResponse>("/api/mcp/call", {
      tool_name: toolName,
      arguments: args,
    }),
  )
}

export function getWorkflows(): Promise<WorkflowDefinition[]> {
  return execute(() =>
    api.get<WorkflowDefinition[]>("/api/workflows"),
  )
}

export function createWorkflow(
  payload: WorkflowCreate,
): Promise<WorkflowDefinition> {
  return execute(() =>
    api.post<WorkflowDefinition>("/api/workflows", payload),
  )
}

export function runWorkflow(
  workflowId: string,
  input: string,
): Promise<WorkflowRunResult> {
  return execute(() =>
    api.post<WorkflowRunResult>(
      `/api/workflows/${workflowId}/run`,
      {
        input,
        context: {},
      },
    ),
  )
}

export function getWorkflowRuns(
  workflowId: string,
): Promise<WorkflowRunResult[]> {
  return execute(() =>
    api.get<WorkflowRunResult[]>(
      `/api/workflows/${workflowId}/runs`,
    ),
  )
}

export function resumeWorkflowRun(
  runId: string,
): Promise<WorkflowRunResult> {
  return execute(() =>
    api.post<WorkflowRunResult>(
      `/api/workflows/runs/${runId}/resume`,
    ),
  )
}

export function getApprovals(
  status?: ApprovalStatus,
): Promise<ApprovalListResponse> {
  return execute(() =>
    api.get<ApprovalListResponse>("/api/approvals", {
      params: status ? { status } : undefined,
    }),
  )
}

export function approveRequest(
  approvalId: string,
  comment: string,
): Promise<ApprovalRequest> {
  return execute(() =>
    api.post<ApprovalRequest>(
      `/api/approvals/${approvalId}/approve`,
      {
        comment: comment || null,
      },
    ),
  )
}

export function rejectRequest(
  approvalId: string,
  comment: string,
): Promise<ApprovalRequest> {
  return execute(() =>
    api.post<ApprovalRequest>(
      `/api/approvals/${approvalId}/reject`,
      {
        comment: comment || null,
      },
    ),
  )
}
export function getSprint4Health():
Promise<Sprint4HealthResponse> {
  return execute(() =>
    api.get<Sprint4HealthResponse>(
      "/api/sprint4/health",
    ),
  )
}