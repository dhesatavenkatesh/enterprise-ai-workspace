export interface AgentDefinition {
  name: string
  description?: string
  capabilities?: string[]
  [key: string]: unknown
}

export interface AgentListResponse {
  agents: AgentDefinition[]
}

export interface AgentExecutionRequest {
  message: string
  agent_name?: string
  agent_names?: string[]
  conversation_id?: string
  context?: Record<string, unknown>
  metadata?: Record<string, unknown>
}

export interface AgentExecutionResponse {
  orchestration_id: string
  mode: "auto" | "single" | "multi"
  routing: {
    selected_agents: string[]
    reason: string
    confidence: number
  }
  results: Record<string, unknown>[]
  final_answer: string
  successful_agents: number
  failed_agents: number
  created_at: string
}

export interface MCPToolParameter {
  name: string
  type: string
  description: string
  required: boolean
  default?: unknown
}

export interface MCPToolDefinition {
  name: string
  description: string
  category: string
  parameters: MCPToolParameter[]
  requires_approval: boolean
  enabled: boolean
}

export interface MCPDiscoveryResponse {
  count: number
  tools: MCPToolDefinition[]
}

export interface MCPToolCallResponse {
  tool_name: string
  success: boolean
  result?: unknown
  error?: string | null
  execution_time_ms: number
  requires_approval: boolean
}

export type WorkflowStepType = "agent" | "mcp_tool"
export type WorkflowStatus = "draft" | "active" | "disabled"
export type WorkflowRunStatus =
  | "pending"
  | "running"
  | "waiting_approval"
  | "completed"
  | "failed"
  | "rejected"

export interface WorkflowStepDefinition {
  id?: string
  name: string
  type: WorkflowStepType
  target: string
  input_template: string
  arguments: Record<string, unknown>
  continue_on_error: boolean
  requires_approval: boolean
  approval_reason?: string | null
}

export interface WorkflowCreate {
  name: string
  description: string
  steps: WorkflowStepDefinition[]
  status: WorkflowStatus
}

export interface WorkflowDefinition extends WorkflowCreate {
  id: string
  owner_id?: string | number | null
  created_at: string
  updated_at: string
}

export interface WorkflowRunResult {
  id: string
  workflow_id: string
  workflow_name: string
  status: WorkflowRunStatus
  initial_input: string
  context: Record<string, unknown>
  conversation_id?: string | null
  final_output?: unknown
  error?: string | null
  step_results: Record<string, unknown>[]
  current_step_index: number
  pending_approval_id?: string | null
  started_at: string
  completed_at?: string | null
}

export type ApprovalStatus =
  | "pending"
  | "approved"
  | "rejected"
  | "cancelled"

export interface ApprovalRequest {
  id: string
  title: string
  description: string
  resource_type: string
  resource_id: string
  requested_by?: string | number | null
  payload: Record<string, unknown>
  status: ApprovalStatus
  decided_by?: string | number | null
  decision_comment?: string | null
  created_at: string
  decided_at?: string | null
}

export interface ApprovalListResponse {
  total: number
  items: ApprovalRequest[]
}

export interface Sprint4ModuleHealth {
  ready: boolean
  message?: string
}

export interface Sprint4HealthResponse {
  status: string
  agents: Sprint4ModuleHealth
  mcp: Sprint4ModuleHealth
  workflows: Sprint4ModuleHealth
  approvals: Sprint4ModuleHealth
}