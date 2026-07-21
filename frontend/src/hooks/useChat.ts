import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query"

import {
  chatService,
} from "@/services/chatService"

import {
  queryKeys,
} from "@/services/queryKeys"

import type {
  ChatMessage,
  SendChatMessageRequest,
} from "@/types/chat"

interface SendChatMessageVariables {
  payload: SendChatMessageRequest
  signal?: AbortSignal
}

export function useSendChatMessage() {
  const queryClient = useQueryClient()

  return useMutation({
    mutationFn: ({
      payload,
      signal,
    }: SendChatMessageVariables) =>
      chatService.sendMessage(
        payload,
        signal,
      ),

    onSuccess: (response) => {
      const conversationId =
        response.conversation_id

      queryClient.setQueryData<
        ChatMessage[]
      >(
        queryKeys.chat.messages(
          conversationId,
        ),
        (
          existingMessages = [],
        ) => {
          const messageIds = new Set(
            existingMessages.map(
              (message) => message.id,
            ),
          )

          const newMessages = [
            response.user_message,
            response.assistant_message,
          ].filter(
            (message) =>
              !messageIds.has(message.id),
          )

          return [
            ...existingMessages,
            ...newMessages,
          ]
        },
      )

      void queryClient.invalidateQueries({
        queryKey:
          queryKeys.chat.conversations(),
      })

      void queryClient.invalidateQueries({
        queryKey:
          queryKeys.chat.conversation(
            conversationId,
          ),
      })

      void queryClient.invalidateQueries({
        queryKey:
          queryKeys.analytics.summary(),
      })

      void queryClient.invalidateQueries({
        queryKey:
          queryKeys.analytics.usage(),
      })
    },
  })
}