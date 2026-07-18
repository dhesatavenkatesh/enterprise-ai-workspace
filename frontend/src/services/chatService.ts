import {
  apiClient,
} from "@/services/apiClient"

import type {
  SendChatMessageRequest,
  SendChatMessageResponse,
} from "@/types/chat"

export const chatService = {
  async sendMessage(
    payload: SendChatMessageRequest,
    signal?: AbortSignal,
  ): Promise<SendChatMessageResponse> {
    const response =
      await apiClient.post<SendChatMessageResponse>(
        "/api/chat",
        payload,
        {
          signal,
        },
      )

    return response.data
  },
}