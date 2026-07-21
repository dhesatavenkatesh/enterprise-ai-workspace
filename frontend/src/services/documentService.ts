import { apiClient } from "@/services/apiClient"

import type {
  DocumentDeleteResponse,
  DocumentIndexResponse,
  DocumentListParams,
  DocumentListResponse,
  DocumentUploadResponse,
  KnowledgeDocument,
  UploadDocumentPayload,
} from "@/types/document"

function createSearchParams(
  params: DocumentListParams,
): URLSearchParams {
  const searchParams = new URLSearchParams()

  searchParams.set(
    "page",
    String(params.page ?? 1),
  )

  searchParams.set(
    "page_size",
    String(params.page_size ?? 20),
  )

  if (params.search?.trim()) {
    searchParams.set(
      "search",
      params.search.trim(),
    )
  }

  if (params.department) {
    searchParams.set(
      "department",
      params.department,
    )
  }

  if (params.status) {
    searchParams.set(
      "status",
      params.status,
    )
  }

  if (params.document_type) {
    searchParams.set(
      "document_type",
      params.document_type,
    )
  }

  return searchParams
}

export const documentService = {
  async getDocuments(
    params: DocumentListParams = {},
  ): Promise<DocumentListResponse> {
    const searchParams =
      createSearchParams(params)

    const response =
      await apiClient.get<DocumentListResponse>(
        `/api/documents?${searchParams.toString()}`,
      )

    return response.data
  },

  async getDocument(
    documentId: string,
  ): Promise<KnowledgeDocument> {
    const response =
      await apiClient.get<KnowledgeDocument>(
        `/api/documents/${documentId}`,
      )

    return response.data
  },

  async uploadDocument(
  payload: UploadDocumentPayload,
): Promise<DocumentUploadResponse> {
  const formData = new FormData()

  formData.append("file", payload.file)

  if (payload.title?.trim()) {
    formData.append(
      "title",
      payload.title.trim(),
    )
  }

  formData.append(
    "department",
    payload.department ?? "General",
  )

  formData.append(
    "document_type",
    payload.document_type ??
      payload.file.name
        .split(".")
        .pop()
        ?.toLowerCase() ??
      "unknown",
  )

  if (payload.description?.trim()) {
    formData.append(
      "description",
      payload.description.trim(),
    )
  }

  const response =
    await apiClient.post<DocumentUploadResponse>(
      "/api/documents/upload",
      formData,
      {
        timeout: 120000,

        // Do not manually set multipart/form-data.
        // The browser must add the boundary automatically.
        headers: {
          "Content-Type": undefined,
        },
      },
    )

  return response.data
},

  async indexDocument(
    documentId: string,
  ): Promise<DocumentIndexResponse> {
    const response =
      await apiClient.post<DocumentIndexResponse>(
        `/api/documents/${documentId}/index`,
      )

    return response.data
  },

  async deleteDocument(
    documentId: string,
  ): Promise<DocumentDeleteResponse> {
    const response =
      await apiClient.delete<DocumentDeleteResponse>(
        `/api/documents/${documentId}`,
      )

    return response.data
  },
}