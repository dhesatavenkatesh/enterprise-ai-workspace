import axios, {
  type AxiosError,
  type AxiosInstance,
} from "axios"


const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  "http://127.0.0.1:8000"


const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    "Content-Type": "application/json",
  },
})


api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token")

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})


export interface DocumentIndexRequest {
  chunk_size?: number
  chunk_overlap?: number
  replace_existing?: boolean
}


export interface DocumentIndexResponse {
  document_id: string
  status: string
  chunks_created: number
  vectors_stored: number
  embedding_model: string
  embedding_dimension: number
  processed_at: string
}


export interface DocumentIndexStatus {
  document_id: string
  status: string
  processing_progress: number
  chunk_count: number
  embedding_model: string | null
  vector_dimension: number | null
  vector_collection: string | null
  indexed: boolean
}


export interface RAGCitation {
  citation_number: number
  document_id: string
  document_title: string
  file_name: string
  chunk_index: number
  content: string
  similarity: number
  department?: string | null
  page_number?: number | null
}


export interface RAGSearchRequest {
  query: string
  top_k?: number
  document_id?: string | null
  department?: string | null
  document_type?: string | null
  minimum_similarity?: number
}


export interface RAGSearchResponse {
  query: string
  results: Record<string, unknown>[]
  citations: RAGCitation[]
  result_count: number
  search_time_ms: number
}


export interface RAGChatRequest {
  query: string
  top_k?: number
  document_id?: string | null
  department?: string | null
  document_type?: string | null
  minimum_similarity?: number
}


export interface RAGChatResponse {
  query: string
  answer: string
  citations: RAGCitation[]
  sources_used: number
  context: string
  search_time_ms: number
}


function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{
      detail?: string
      message?: string
    }>

    return (
      axiosError.response?.data?.detail ??
      axiosError.response?.data?.message ??
      axiosError.message ??
      "Request failed"
    )
  }

  if (error instanceof Error) {
    return error.message
  }

  return "An unexpected error occurred"
}


export async function indexDocument(
  documentId: string,
  payload: DocumentIndexRequest = {},
): Promise<DocumentIndexResponse> {
  try {
    const response = await api.post<DocumentIndexResponse>(
      `/api/rag/documents/${documentId}/index`,
      {
        chunk_size: payload.chunk_size ?? 512,
        chunk_overlap: payload.chunk_overlap ?? 50,
        replace_existing:
          payload.replace_existing ?? true,
      },
    )

    return response.data
  } catch (error) {
    throw new Error(getErrorMessage(error))
  }
}


export async function getDocumentIndexStatus(
  documentId: string,
): Promise<DocumentIndexStatus> {
  try {
    const response = await api.get<DocumentIndexStatus>(
      `/api/rag/documents/${documentId}/index-status`,
    )

    return response.data
  } catch (error) {
    throw new Error(getErrorMessage(error))
  }
}


export async function deleteDocumentIndex(
  documentId: string,
): Promise<Record<string, unknown>> {
  try {
    const response = await api.delete<
      Record<string, unknown>
    >(`/api/rag/documents/${documentId}/index`)

    return response.data
  } catch (error) {
    throw new Error(getErrorMessage(error))
  }
}


export async function searchDocuments(
  payload: RAGSearchRequest,
): Promise<RAGSearchResponse> {
  try {
    const response = await api.post<RAGSearchResponse>(
      "/api/rag/search",
      {
        query: payload.query,
        top_k: payload.top_k ?? 5,
        document_id: payload.document_id ?? null,
        department: payload.department ?? null,
        document_type:
          payload.document_type ?? null,
        minimum_similarity:
          payload.minimum_similarity ?? 0.1,
      },
    )

    return response.data
  } catch (error) {
    throw new Error(getErrorMessage(error))
  }
}


export async function askRAGQuestion(
  payload: RAGChatRequest,
): Promise<RAGChatResponse> {
  try {
    const response = await api.post<RAGChatResponse>(
      "/api/rag/chat",
      {
        query: payload.query,
        top_k: payload.top_k ?? 5,
        document_id: payload.document_id ?? null,
        department: payload.department ?? null,
        document_type:
          payload.document_type ?? null,
        minimum_similarity:
          payload.minimum_similarity ?? 0.1,
      },
    )

    return response.data
  } catch (error) {
    throw new Error(getErrorMessage(error))
  }
}


export default api