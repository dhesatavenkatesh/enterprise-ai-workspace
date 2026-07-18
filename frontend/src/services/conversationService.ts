import {
  apiClient,
} from "@/services/apiClient"

import type {
  ChatMessage,
} from "@/types/chat"

import type {
  Conversation,
  ConversationListResponse,
  ConversationQueryParams,
  DeleteConversationResponse,
  RenameConversationRequest,
} from "@/types/conversation"


function normalizeConversationList(
  data:
    | Conversation[]
    | ConversationListResponse,
  page: number,
  pageSize: number,
): ConversationListResponse {
  if (Array.isArray(data)) {
    const total = data.length

    return {
      items: data,
      total,
      page,
      page_size: pageSize,
      total_pages:
        total === 0
          ? 0
          : Math.ceil(total / pageSize),
    }
  }

  return data
}


export const conversationService = {
  /**
   * Return normal or archived conversations.
   *
   * Backend:
   * GET /api/chat/conversations
   */
  async listConversations(
    params: ConversationQueryParams = {},
  ): Promise<ConversationListResponse> {
    const page = params.page ?? 1
    const pageSize = params.page_size ?? 20

    const response =
      await apiClient.get<
        | Conversation[]
        | ConversationListResponse
      >(
        "/api/chat/conversations",
        {
          params: {
            page,
            page_size: pageSize,
            search:
              params.search?.trim() ||
              undefined,
            archived:
              params.archived ?? false,
          },
        },
      )

    return normalizeConversationList(
      response.data,
      page,
      pageSize,
    )
  },

  /**
   * Return one conversation with its messages.
   *
   * Backend:
   * GET /api/chat/{conversation_id}
   */
  async getConversation(
    conversationId: string,
  ): Promise<Conversation> {
    const response =
      await apiClient.get<Conversation>(
        `/api/chat/${conversationId}`,
      )

    return response.data
  },

  /**
   * The current backend conversation detail endpoint
   * already includes the message history.
   */
  async getMessages(
    conversationId: string,
  ): Promise<ChatMessage[]> {
    const conversation =
      await this.getConversation(
        conversationId,
      )

    return conversation.messages ?? []
  },

  /**
   * Rename a conversation.
   *
   * Backend:
   * PUT /api/chat/{conversation_id}/rename
   */
  async renameConversation(
    conversationId: string,
    payload: RenameConversationRequest,
  ): Promise<Conversation> {
    const response =
      await apiClient.put<Conversation>(
        `/api/chat/${conversationId}/rename`,
        payload,
      )

    return response.data
  },

  /**
   * Delete a conversation.
   *
   * Backend:
   * DELETE /api/chat/{conversation_id}
   */
  async deleteConversation(
    conversationId: string,
  ): Promise<DeleteConversationResponse> {
    const response =
      await apiClient.delete<
        DeleteConversationResponse
      >(
        `/api/chat/${conversationId}`,
      )

    return response.data
  },

  /**
   * Archive a conversation.
   *
   * Backend:
   * PUT /api/chat/{conversation_id}/archive
   */
  async archiveConversation(
    conversationId: string,
  ): Promise<Conversation> {
    const response =
      await apiClient.put<Conversation>(
        `/api/chat/${conversationId}/archive`,
      )

    return response.data
  },

  /**
   * Restore an archived conversation.
   *
   * Backend:
   * PUT /api/chat/{conversation_id}/restore
   */
  async restoreConversation(
    conversationId: string,
  ): Promise<Conversation> {
    const response =
      await apiClient.put<Conversation>(
        `/api/chat/${conversationId}/restore`,
      )

    return response.data
  },
}