import {
  apiClient,
} from "@/services/apiClient"

export interface OrchestratorRequest {
  query: string
}

export interface OrchestratorResponse {
  status: string
  agent: string
  tools: string[]
  query: string
  answer: string
  duration_ms: number
  user_id: string | null
}

export const orchestratorService = {
  async execute(
    payload: OrchestratorRequest,
  ): Promise<OrchestratorResponse> {
    const response =
      await apiClient.post<OrchestratorResponse>(
        "/api/orchestrator/execute",
        payload,
      )

    return response.data
  },
}