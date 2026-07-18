export type MessageRole =
  | "user"
  | "assistant"
  | "system"

export type LLMProvider =
  | "groq"
  | "openai"
  | "ollama"

export interface ChatMessage {
  id: string
  conversation_id: string
  role: MessageRole
  content: string
  token_count: number
  prompt_tokens: number
  completion_tokens: number
  provider: string | null
  model_name: string | null
  created_at: string
}

export interface SendChatMessageRequest {
  message: string
  conversation_id?: string | null
  prompt_template_id?: string | null
  provider?: LLMProvider
  model_name?: string
  temperature?: number
}

export interface SendChatMessageResponse {
  conversation_id: string
  conversation_title: string
  user_message: ChatMessage
  assistant_message: ChatMessage
  total_tokens: number
}

export interface ChatComposerValues {
  message: string
  provider: LLMProvider
  model_name: string
  temperature: number
  prompt_template_id: string | null
}