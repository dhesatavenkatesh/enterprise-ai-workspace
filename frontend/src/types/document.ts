export type DocumentStatus =
  | "uploaded"
  | "processing"
  | "completed"
  | "indexed"
  | "failed"

export interface KnowledgeDocument {
  id: string
  user_id: number

  title: string
  file_name: string
  original_file_name?: string | null
  file_path?: string | null

  document_type: string
  department?: string | null
  description?: string | null

  file_size: number
  status: DocumentStatus | string

  processing_progress: number
  chunk_count: number

  embedding_model?: string | null
  vector_dimension?: number | null
  vector_collection?: string | null

  version_number?: number
  is_deleted?: boolean

  created_at: string
  updated_at?: string
}

export interface DocumentListResponse {
  items: KnowledgeDocument[]
  total: number
  page: number
  page_size: number
  total_pages?: number
}

export interface DocumentUploadResponse {
  message: string
  document: KnowledgeDocument
}

export interface DocumentDeleteResponse {
  message: string
  document_id: string
}

export interface DocumentIndexResponse {
  message: string
  document_id: string
  status: string
  chunk_count?: number
}

export interface DocumentListParams {
  page?: number
  page_size?: number
  search?: string
  department?: string
  status?: string
  document_type?: string
}

export interface UploadDocumentPayload {
  file: File
  title?: string
  department?: string
  document_type?: string
  description?: string
}