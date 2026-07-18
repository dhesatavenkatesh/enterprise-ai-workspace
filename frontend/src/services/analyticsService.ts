import {
  apiClient,
} from "@/services/apiClient"

import type {
  AnalyticsDateParams,
  ChatAnalyticsSummary,
  ChatUsageAnalytics,
} from "@/types/analytics"

export const analyticsService = {
  async getSummary(
    params: AnalyticsDateParams = {},
  ): Promise<ChatAnalyticsSummary> {
    const response =
      await apiClient.get<ChatAnalyticsSummary>(
        "/api/chat/analytics/summary",
        {
          params,
        },
      )

    return response.data
  },

  async getUsage(
    params: AnalyticsDateParams = {},
  ): Promise<ChatUsageAnalytics> {
    const response =
      await apiClient.get<ChatUsageAnalytics>(
        "/api/chat/analytics/usage",
        {
          params,
        },
      )

    return response.data
  },
}