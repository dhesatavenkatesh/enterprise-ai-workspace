import {
  BrainCircuit,
  Menu,
  MessageSquareText,
  Plus,
  Sparkles,
  X,
} from "lucide-react"

import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react"

import {
  ChatComposer,
} from "@/components/chat/ChatComposer"

import {
  ChatMessage,
} from "@/components/chat/ChatMessage"

import {
  ConversationSidebar,
} from "@/components/chat/ConversationSidebar"

import {
  TypingIndicator,
} from "@/components/chat/TypingIndicator"

import {
  Button,
} from "@/components/ui/button"

import {
  useSendChatMessage,
} from "@/hooks/useChat"

import {
  useConversationMessages,
} from "@/hooks/useConversations"

import {
  usePromptTemplates,
} from "@/hooks/usePromptTemplates"

import {
  cn,
} from "@/lib/utils"

import {
  useAuthStore,
} from "@/store/authStore"

import {
  getApiError,
} from "@/utils/getApiError"

import type {
  ChatMessage as ChatMessageType,
  LLMProvider,
} from "@/types/chat"

interface ComposerValues {
  message: string
  provider: LLMProvider
  model_name: string
  temperature: number
  prompt_template_id:
    | string
    | null
}

const starterPrompts = [
  "Summarize the key priorities for this week.",
  "Create a professional project status update.",
  "Explain our enterprise AI architecture.",
  "Draft a clear email for a project delay.",
]

function createTemporaryMessage(
  content: string,
): ChatMessageType {
  return {
    id: `temporary-${Date.now()}`,
    conversation_id: "",
    role: "user",
    content,
    token_count: 0,
    prompt_tokens: 0,
    completion_tokens: 0,
    provider: null,
    model_name: null,
    created_at:
      new Date().toISOString(),
  }
}

function isRequestCancelled(
  error: unknown,
): boolean {
  if (
    error instanceof DOMException &&
    error.name === "AbortError"
  ) {
    return true
  }

  if (
    typeof error !== "object" ||
    error === null
  ) {
    return false
  }

  const possibleError =
    error as {
      name?: string
      code?: string
      message?: string
    }

  return (
    possibleError.name ===
      "AbortError" ||
    possibleError.name ===
      "CanceledError" ||
    possibleError.code ===
      "ERR_CANCELED" ||
    possibleError.message ===
      "canceled"
  )
}

export function AIChatPage() {
  const messagesEndRef =
    useRef<HTMLDivElement | null>(
      null,
    )

  const abortControllerRef =
    useRef<AbortController | null>(
      null,
    )

  const user = useAuthStore(
    (state) => state.user,
  )

  const [
    selectedConversationId,
    setSelectedConversationId,
  ] = useState<string | null>(
    null,
  )

  const [
    mobileSidebarOpen,
    setMobileSidebarOpen,
  ] = useState(false)

  const [
    temporaryMessage,
    setTemporaryMessage,
  ] =
    useState<ChatMessageType | null>(
      null,
    )

  const [
    composerInitialMessage,
    setComposerInitialMessage,
  ] = useState("")

  const [error, setError] =
    useState("")

  const sendMessage =
    useSendChatMessage()

  const messagesQuery =
    useConversationMessages(
      selectedConversationId,
    )

  const templatesQuery =
    usePromptTemplates({
      page: 1,
      page_size: 100,
      status: "active",
    })

  const messages =
    useMemo(() => {
      const savedMessages =
        messagesQuery.data ?? []

      if (!temporaryMessage) {
        return savedMessages
      }

      return [
        ...savedMessages,
        temporaryMessage,
      ]
    }, [
      messagesQuery.data,
      temporaryMessage,
    ])

  const handleStopGeneration =
    (): void => {
      const controller =
        abortControllerRef.current

      if (!controller) {
        return
      }

      controller.abort()
      abortControllerRef.current = null

      setTemporaryMessage(null)
      setError("")
    }

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView(
      {
        behavior: "smooth",
      },
    )
  }, [
    messages,
    sendMessage.isPending,
  ])

  useEffect(() => {
    return () => {
      abortControllerRef.current?.abort()
      abortControllerRef.current = null
    }
  }, [])

  const handleNewConversation =
    (): void => {
      handleStopGeneration()

      setSelectedConversationId(
        null,
      )

      setTemporaryMessage(null)
      setComposerInitialMessage("")
      setError("")
      setMobileSidebarOpen(false)
    }

  const handleSelectConversation = (
    conversationId: string,
  ): void => {
    handleStopGeneration()

    setSelectedConversationId(
      conversationId,
    )

    setTemporaryMessage(null)
    setComposerInitialMessage("")
    setError("")
    setMobileSidebarOpen(false)
  }

  const handleStarterPrompt = (
    prompt: string,
  ): void => {
    if (sendMessage.isPending) {
      return
    }

    setComposerInitialMessage(
      prompt,
    )
  }

  const handleSend =
    async (
      values: ComposerValues,
    ): Promise<boolean> => {
      if (sendMessage.isPending) {
        return false
      }

      setError("")
      setComposerInitialMessage("")

      const controller =
        new AbortController()

      abortControllerRef.current =
        controller

      const pendingMessage =
        createTemporaryMessage(
          values.message,
        )

      setTemporaryMessage(
        pendingMessage,
      )

      try {
        const response =
          await sendMessage.mutateAsync({
            payload: {
              message: values.message,
              conversation_id: selectedConversationId,
              prompt_template_id:
              values.prompt_template_id,
              provider: values.provider,
              model_name: values.model_name,
              temperature: values.temperature,

              top_k: 5,
              department: null,
              document_type: null,
              minimum_similarity: 0,
            },

            signal:
              controller.signal,
          })

        if (
          controller.signal.aborted
        ) {
          setTemporaryMessage(null)
          return false
        }

        setSelectedConversationId(
          response.conversation_id,
        )

        setTemporaryMessage(null)

        return true
      } catch (sendError) {
        setTemporaryMessage(null)

        if (
          isRequestCancelled(
            sendError,
          )
        ) {
          setError("")
          return false
        }

        setError(
          getApiError(
            sendError,
            "The AI response could not be generated.",
          ),
        )

        return false
      } finally {
        if (
          abortControllerRef.current ===
          controller
        ) {
          abortControllerRef.current =
            null
        }
      }
    }

  const hasConversation =
    Boolean(
      selectedConversationId,
    )

  const hasMessages =
    messages.length > 0

  const firstName =
    user?.name
      ?.trim()
      .split(/\s+/)[0] ||
    "there"

  return (
    <div className="-m-4 h-[calc(100vh-4.5rem)] overflow-hidden sm:-m-6 lg:-m-8">
      <div className="flex h-full min-h-0 border-t bg-background">
        <div
          className={cn(
            "fixed inset-y-0 left-0 z-50 w-78 bg-background shadow-xl transition-transform lg:static lg:z-auto lg:w-72 lg:translate-x-0 lg:shadow-none xl:w-80",
            mobileSidebarOpen
              ? "translate-x-0"
              : "-translate-x-full",
          )}
        >
          <div className="absolute right-2 top-2 z-10 lg:hidden">
            <Button
              type="button"
              variant="ghost"
              size="icon"
              aria-label="Close conversation list"
              onClick={() => {
                setMobileSidebarOpen(
                  false,
                )
              }}
            >
              <X className="h-5 w-5" />
            </Button>
          </div>

          <ConversationSidebar
            activeConversationId={
              selectedConversationId
            }
            onSelectConversation={
              handleSelectConversation
            }
            onNewChat={
              handleNewConversation
            }
          />
        </div>

        {mobileSidebarOpen && (
          <button
            type="button"
            aria-label="Close conversation overlay"
            onClick={() => {
              setMobileSidebarOpen(
                false,
              )
            }}
            className="fixed inset-0 z-40 bg-black/40 lg:hidden"
          />
        )}

        <main className="flex min-w-0 flex-1 flex-col">
          <header className="flex h-16 shrink-0 items-center justify-between border-b px-3 sm:px-5">
            <div className="flex min-w-0 items-center gap-2.5">
              <Button
                type="button"
                variant="ghost"
                size="icon"
                className="lg:hidden"
                aria-label="Open conversation list"
                onClick={() => {
                  setMobileSidebarOpen(
                    true,
                  )
                }}
              >
                <Menu className="h-5 w-5" />
              </Button>

              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-violet-100 text-violet-700 dark:bg-violet-950/50 dark:text-violet-300">
                <BrainCircuit className="h-5 w-5" />
              </div>

              <div className="min-w-0">
                <h1 className="truncate text-sm font-semibold sm:text-base">
                  {hasConversation
                    ? "AI Conversation"
                    : "New Conversation"}
                </h1>

                <p className="truncate text-xs text-muted-foreground">
                  Enterprise AI Assistant
                </p>
              </div>
            </div>

            <Button
              type="button"
              variant="outline"
              size="sm"
              disabled={
                sendMessage.isPending
              }
              onClick={
                handleNewConversation
              }
            >
              <Plus className="h-4 w-4" />

              <span className="hidden sm:inline">
                New chat
              </span>
            </Button>
          </header>

          <section className="min-h-0 flex-1 overflow-y-auto">
            {messagesQuery.isLoading && (
              <div className="flex h-full items-center justify-center">
                <div className="text-center">
                  <div className="mx-auto h-8 w-8 animate-spin rounded-full border-[3px] border-violet-200 border-t-violet-600" />

                  <p className="mt-3 text-sm text-muted-foreground">
                    Loading conversation...
                  </p>
                </div>
              </div>
            )}

            {!messagesQuery.isLoading &&
              messagesQuery.isError && (
                <div className="flex h-full items-center justify-center px-4">
                  <div className="max-w-md rounded-xl border border-destructive/20 bg-destructive/10 p-4 text-center">
                    <p className="text-sm font-medium text-destructive">
                      Unable to load this
                      conversation.
                    </p>

                    <p className="mt-1 text-xs text-muted-foreground">
                      Select another
                      conversation or start a
                      new chat.
                    </p>
                  </div>
                </div>
              )}

            {!messagesQuery.isLoading &&
              !messagesQuery.isError &&
              !hasMessages &&
              !sendMessage.isPending && (
                <div className="flex min-h-full items-center justify-center px-4 py-10">
                  <div className="w-full max-w-3xl text-center">
                    <div className="mx-auto flex h-18 w-18 items-center justify-center rounded-3xl bg-gradient-to-br from-violet-600 to-indigo-600 text-white shadow-lg shadow-violet-500/20">
                      <Sparkles className="h-8 w-8" />
                    </div>

                    <h2 className="mt-6 text-2xl font-bold tracking-tight sm:text-3xl">
                      How can I help you,{" "}
                      {firstName}?
                    </h2>

                    <p className="mx-auto mt-3 max-w-xl text-sm leading-6 text-muted-foreground sm:text-base">
                      Ask questions, generate
                      content, analyze ideas or
                      use a reusable enterprise
                      prompt template.
                    </p>

                    <div className="mt-8 grid gap-3 text-left sm:grid-cols-2">
                      {starterPrompts.map(
                        (prompt) => (
                          <button
                            key={prompt}
                            type="button"
                            disabled={
                              sendMessage.isPending
                            }
                            onClick={() => {
                              handleStarterPrompt(
                                prompt,
                              )
                            }}
                            className="rounded-xl border bg-card p-4 text-sm leading-5 transition hover:border-violet-300 hover:bg-violet-50/50 focus:outline-none focus:ring-2 focus:ring-violet-500/30 disabled:cursor-not-allowed disabled:opacity-50 dark:hover:bg-violet-950/20"
                          >
                            <MessageSquareText className="mb-3 h-5 w-5 text-violet-600" />

                            {prompt}
                          </button>
                        ),
                      )}
                    </div>
                  </div>
                </div>
              )}

            {hasMessages && (
              <div className="mx-auto w-full max-w-4xl space-y-6 px-4 py-6 md:px-6 md:py-8">
                {messages.map(
                  (message) => (
                    <ChatMessage
                      key={message.id}
                      message={message}
                    />
                  ),
                )}

                {sendMessage.isPending && (
                  <TypingIndicator />
                )}

                <div
                  ref={messagesEndRef}
                />
              </div>
            )}

            {error && (
              <div className="mx-auto mb-4 max-w-4xl px-4">
                <div className="rounded-xl border border-destructive/20 bg-destructive/10 px-4 py-3 text-sm text-destructive">
                  {error}
                </div>
              </div>
            )}
          </section>

          <ChatComposer
            disabled={
              sendMessage.isPending
            }
            isGenerating={
              sendMessage.isPending
            }
            templates={
              templatesQuery.data
                ?.items ?? []
            }
            initialMessage={
              composerInitialMessage
            }
            onInitialMessageConsumed={() => {
              setComposerInitialMessage(
                "",
              )
            }}
            onStop={
              handleStopGeneration
            }
            onSend={handleSend}
          />
        </main>
      </div>
    </div>
  )
}

export default AIChatPage