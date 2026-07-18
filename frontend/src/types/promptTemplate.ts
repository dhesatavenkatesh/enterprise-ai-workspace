export type PromptTemplateStatus =
  | "active"
  | "inactive"
  | "archived"

export interface PromptTemplate {
  id: string
  name: string
  description: string | null
  content: string
  category: string | null
  status: PromptTemplateStatus
  is_public: boolean
  usage_count: number
  user_id: number
  created_at: string
  updated_at: string
}

export interface PromptTemplateListResponse {
  items: PromptTemplate[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface PromptTemplateQueryParams {
  page?: number
  page_size?: number
  search?: string
  category?: string
  status?: PromptTemplateStatus
  is_public?: boolean
}

export interface CreatePromptTemplateRequest {
  name: string
  description?: string | null
  content: string
  category?: string | null
  status?: PromptTemplateStatus
  is_public?: boolean
}

export interface UpdatePromptTemplateRequest {
  name?: string
  description?: string | null
  content?: string
  category?: string | null
  status?: PromptTemplateStatus
  is_public?: boolean
}