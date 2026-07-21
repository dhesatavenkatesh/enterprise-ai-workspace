export interface AgentAnalyticsSummary {
  total_executions: number
  successful_runs: number
  failed_runs: number
  success_rate: number
  average_response_time_ms: number
  total_input_tokens: number
  total_output_tokens: number
  total_tokens: number
  average_workflow_duration_ms: number
}

export interface AgentLeaderboardItem {
  rank: number
  agent_name: string
  total_executions: number
  successful_runs: number
  failed_runs: number
  success_rate: number
  average_response_time_ms: number
  token_usage: number
}

export interface AgentToolUsage {
  tool_name: string
  usage_count: number
}

export interface AgentTrend {
  date: string
  total_executions: number
  successful_runs: number
  failed_runs: number
  token_usage: number
  average_response_time_ms: number
}

export interface AgentExecutionMetric {
  id: string
  agent_name: string
  status: "success" | "failed"
  response_time_ms: number
  input_tokens: number
  output_tokens: number
  tool_names: string[]
  workflow_id: string | null
  workflow_duration_ms: number | null
  error_message: string | null
  created_at: string
}

export interface AgentAnalyticsResponse {
  summary: AgentAnalyticsSummary
  leaderboard: AgentLeaderboardItem[]
  tool_usage: AgentToolUsage[]
  trends: AgentTrend[]
  recent_executions: AgentExecutionMetric[]
}