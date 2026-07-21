import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query"

import {
  documentService,
} from "@/services/documentService"

import type {
  DocumentListParams,
  UploadDocumentPayload,
} from "@/types/document"

export const documentKeys = {
  all: ["documents"] as const,

  lists: () =>
    [
      ...documentKeys.all,
      "list",
    ] as const,

  list: (
    params: DocumentListParams,
  ) =>
    [
      ...documentKeys.lists(),
      params,
    ] as const,

  details: () =>
    [
      ...documentKeys.all,
      "detail",
    ] as const,

  detail: (
    documentId: string,
  ) =>
    [
      ...documentKeys.details(),
      documentId,
    ] as const,
}

export function useDocuments(
  params: DocumentListParams,
) {
  return useQuery({
    queryKey:
      documentKeys.list(params),

    queryFn: () =>
      documentService.getDocuments(
        params,
      ),

    refetchInterval: (query) => {
      const documents =
        query.state.data?.items ?? []

      const hasActiveProcessing =
        documents.some(
          (document) =>
            document.status ===
              "uploaded" ||
            document.status ===
              "processing",
        )

      return hasActiveProcessing
        ? 3000
        : false
    },
  })
}

export function useDocument(
  documentId: string | null,
) {
  return useQuery({
    queryKey:
      documentKeys.detail(
        documentId ?? "",
      ),

    queryFn: () =>
      documentService.getDocument(
        documentId!,
      ),

    enabled: Boolean(documentId),
  })
}

export function useUploadDocument() {
  const queryClient =
    useQueryClient()

  return useMutation({
    mutationFn: (
      payload: UploadDocumentPayload,
    ) =>
      documentService.uploadDocument(
        payload,
      ),

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey:
          documentKeys.all,
      })
    },
  })
}

export function useIndexDocument() {
  const queryClient =
    useQueryClient()

  return useMutation({
    mutationFn: (
      documentId: string,
    ) =>
      documentService.indexDocument(
        documentId,
      ),

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey:
          documentKeys.all,
      })
    },
  })
}

export function useDeleteDocument() {
  const queryClient =
    useQueryClient()

  return useMutation({
    mutationFn: (
      documentId: string,
    ) =>
      documentService.deleteDocument(
        documentId,
      ),

    onSuccess: async () => {
      await queryClient.invalidateQueries({
        queryKey:
          documentKeys.all,
      })
    },
  })
}