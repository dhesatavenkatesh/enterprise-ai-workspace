import type {
  ChatMessage,
} from "@/types/chat"

export interface Conversation {
  id: string
  user_id?: number
  title: string
  is_archived: boolean
  archived_at?: string | null
  is_pinned?: boolean
  total_tokens?: number
  created_at: string
  updated_at: string
  messages?: ChatMessage[]
}

export interface ConversationListResponse {
  items: Conversation[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface ConversationQueryParams {
  page?: number
  page_size?: number
  search?: string
}

export interface RenameConversationRequest {
  title: string
}

export interface DeleteConversationResponse {
  message: string
  conversation_id: string
}

export interface ConversationQueryParams {
  page?: number
  page_size?: number
  search?: string
  archived?: boolean
}
