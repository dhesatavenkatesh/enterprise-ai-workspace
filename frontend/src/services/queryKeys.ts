import type {
  AnalyticsDateParams,
} from "@/types/analytics"

import type {
  ConversationQueryParams,
} from "@/types/conversation"

import type {
  PromptTemplateQueryParams,
} from "@/types/promptTemplate"

export const queryKeys = {
  auth: {
    all: [
      "auth",
    ] as const,

    currentUser: [
      "auth",
      "current-user",
    ] as const,
  },

  users: {
    all: [
      "users",
    ] as const,
  },

  dashboard: {
    all: [
      "dashboard",
    ] as const,

    statistics: [
      "dashboard",
      "statistics",
    ] as const,
  },

  chat: {
    all: [
      "chat",
    ] as const,

    conversations: (
      params:
        ConversationQueryParams = {},
    ) => [
      "chat",
      "conversations",
      params,
    ] as const,

    conversation: (
      conversationId: string,
    ) => [
      "chat",
      "conversation",
      conversationId,
    ] as const,

    messages: (
      conversationId: string,
    ) => [
      "chat",
      "messages",
      conversationId,
    ] as const,
  },

  promptTemplates: {
    all: [
      "prompt-templates",
    ] as const,

    list: (
      params:
        PromptTemplateQueryParams = {},
    ) => [
      "prompt-templates",
      "list",
      params,
    ] as const,

    detail: (
      templateId: string,
    ) => [
      "prompt-templates",
      "detail",
      templateId,
    ] as const,
  },

  analytics: {
    all: [
      "chat-analytics",
    ] as const,

    summary: (
      params:
        AnalyticsDateParams = {},
    ) => [
      "chat-analytics",
      "summary",
      params,
    ] as const,

    usage: (
      params:
        AnalyticsDateParams = {},
    ) => [
      "chat-analytics",
      "usage",
      params,
    ] as const,
  },
}