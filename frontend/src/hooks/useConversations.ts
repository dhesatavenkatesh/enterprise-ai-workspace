import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query"

import {
  conversationService,
} from "@/services/conversationService"

import {
  queryKeys,
} from "@/services/queryKeys"

import type {
  ConversationQueryParams,
  RenameConversationRequest,
} from "@/types/conversation"

export function useConversations(
  params: ConversationQueryParams = {},
) {
  return useQuery({
    queryKey:
      queryKeys.chat.conversations(
        params,
      ),

    queryFn: () =>
      conversationService.listConversations(
        params,
      ),

    staleTime: 30_000,
  })
}

export function useConversation(
  conversationId:
    | string
    | null
    | undefined,
) {
  return useQuery({
    queryKey:
      queryKeys.chat.conversation(
        conversationId ?? "",
      ),

    queryFn: () =>
      conversationService.getConversation(
        conversationId as string,
      ),

    enabled: Boolean(
      conversationId,
    ),
  })
}

export function useConversationMessages(
  conversationId:
    | string
    | null
    | undefined,
) {
  return useQuery({
    queryKey:
      queryKeys.chat.messages(
        conversationId ?? "",
      ),

    queryFn: () =>
      conversationService.getMessages(
        conversationId as string,
      ),

    enabled: Boolean(
      conversationId,
    ),

    staleTime: 10_000,
  })
}

interface RenameConversationVariables {
  conversationId: string
  payload: RenameConversationRequest
}

export function useRenameConversation() {
  const queryClient =
    useQueryClient()

  return useMutation({
    mutationFn: ({
      conversationId,
      payload,
    }: RenameConversationVariables) =>
      conversationService.renameConversation(
        conversationId,
        payload,
      ),

    onSuccess: (
      updatedConversation,
    ) => {
      queryClient.setQueryData(
        queryKeys.chat.conversation(
          updatedConversation.id,
        ),
        updatedConversation,
      )

      void queryClient.invalidateQueries({
        queryKey:
          queryKeys.chat.all,
      })
    },
  })
}

export function useDeleteConversation() {
  const queryClient =
    useQueryClient()

  return useMutation({
    mutationFn: (
      conversationId: string,
    ) =>
      conversationService.deleteConversation(
        conversationId,
      ),

    onSuccess: () => {
      void queryClient.invalidateQueries({
        queryKey:
          queryKeys.chat.all,
      })
    },
  })
}