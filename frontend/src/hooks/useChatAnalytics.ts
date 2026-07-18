import {
  useQuery,
} from "@tanstack/react-query"

import {
  analyticsService,
} from "@/services/analyticsService"

import {
  queryKeys,
} from "@/services/queryKeys"

import type {
  AnalyticsDateParams,
} from "@/types/analytics"

export function useChatAnalyticsSummary(
  params: AnalyticsDateParams = {},
) {
  return useQuery({
    queryKey:
      queryKeys.analytics.summary(
        params,
      ),

    queryFn: () =>
      analyticsService.getSummary(
        params,
      ),

    staleTime: 60_000,
  })
}

export function useChatUsageAnalytics(
  params: AnalyticsDateParams = {},
) {
  return useQuery({
    queryKey:
      queryKeys.analytics.usage(
        params,
      ),

    queryFn: () =>
      analyticsService.getUsage(
        params,
      ),

    staleTime: 60_000,
  })
}