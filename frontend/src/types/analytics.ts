export interface ProviderUsage {
  provider: string
  message_count: number
  total_tokens: number
  prompt_tokens: number
  completion_tokens: number
}

export interface ModelUsage {
  model_name: string
  provider: string
  message_count: number
  total_tokens: number
}

export interface DailyChatActivity {
  date: string
  conversations: number
  messages: number
  total_tokens: number
}

export interface ChatAnalyticsSummary {
  total_conversations: number
  total_messages: number
  user_messages: number
  assistant_messages: number
  total_tokens: number
  prompt_tokens: number
  completion_tokens: number
  average_tokens_per_message: number
}

export interface ChatUsageAnalytics {
  providers: ProviderUsage[]
  models: ModelUsage[]
  daily_activity: DailyChatActivity[]
}

export interface AnalyticsDateParams {
  start_date?: string
  end_date?: string
  days?: number
}