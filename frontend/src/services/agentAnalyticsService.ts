import api from "@/services/api"

import type {
  AgentAnalyticsResponse,
} from "@/types/agentAnalytics"

export async function getAgentAnalytics(
  days = 7,
): Promise<AgentAnalyticsResponse> {
  const response =
    await api.get<AgentAnalyticsResponse>(
      "/api/analytics/agents",
      {
        params: {
          days,
        },
      },
    )

  return response.data
}