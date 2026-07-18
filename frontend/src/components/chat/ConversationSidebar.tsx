import {
  useEffect,
  useMemo,
  useState,
} from "react"

import {
  Archive,
  Check,
  Loader2,
  MessageSquare,
  MoreHorizontal,
  Pencil,
  Plus,
  RotateCcw,
  Search,
  Trash2,
  X,
} from "lucide-react"

import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query"

import {
  conversationService,
} from "@/services/conversationService"

import type {
  Conversation,
} from "@/types/conversation"


interface ConversationSidebarProps {
  activeConversationId:
    | string
    | null

  onSelectConversation: (
    conversationId: string,
  ) => void

  onNewChat: () => void

  className?: string
}


function formatConversationDate(
  dateValue?: string | null,
): string {
  if (!dateValue) {
    return ""
  }

  const date = new Date(dateValue)

  if (Number.isNaN(date.getTime())) {
    return ""
  }

  const today = new Date()

  const isToday =
    date.toDateString() ===
    today.toDateString()

  if (isToday) {
    return date.toLocaleTimeString(
      [],
      {
        hour: "2-digit",
        minute: "2-digit",
      },
    )
  }

  return date.toLocaleDateString(
    [],
    {
      month: "short",
      day: "numeric",
    },
  )
}


export function ConversationSidebar({
  activeConversationId,
  onSelectConversation,
  onNewChat,
  className = "",
}: ConversationSidebarProps) {
  const queryClient =
    useQueryClient()

  const [
    searchValue,
    setSearchValue,
  ] = useState("")

  const [
    debouncedSearch,
    setDebouncedSearch,
  ] = useState("")

  const [
    showArchived,
    setShowArchived,
  ] = useState(false)

  const [
    editingConversationId,
    setEditingConversationId,
  ] = useState<string | null>(
    null,
  )

  const [
    editedTitle,
    setEditedTitle,
  ] = useState("")

  const [
    openedMenuId,
    setOpenedMenuId,
  ] = useState<string | null>(
    null,
  )

  const conversationsQueryKey =
    useMemo(
      () => [
        "conversations",
        {
          page: 1,
          page_size: 100,
          search: debouncedSearch,
          archived: showArchived,
        },
      ],
      [
        debouncedSearch,
        showArchived,
      ],
    )

  useEffect(() => {
    const timer = window.setTimeout(
      () => {
        setDebouncedSearch(
          searchValue.trim(),
        )
      },
      300,
    )

    return () => {
      window.clearTimeout(timer)
    }
  }, [searchValue])

  const conversationsQuery =
    useQuery({
      queryKey:
        conversationsQueryKey,

      queryFn: () =>
        conversationService
          .listConversations({
            page: 1,
            page_size: 100,
            search:
              debouncedSearch ||
              undefined,
            archived: showArchived,
          }),

      staleTime: 15_000,
    })

  const refreshConversations =
    async () => {
      await queryClient
        .invalidateQueries({
          queryKey: [
            "conversations",
          ],
        })
    }

  const renameMutation =
    useMutation({
      mutationFn: ({
        conversationId,
        title,
      }: {
        conversationId: string
        title: string
      }) =>
        conversationService
          .renameConversation(
            conversationId,
            {
              title,
            },
          ),

      onSuccess: async () => {
        setEditingConversationId(
          null,
        )

        setEditedTitle("")

        setOpenedMenuId(null)

        await refreshConversations()
      },
    })

  const deleteMutation =
    useMutation({
      mutationFn: (
        conversationId: string,
      ) =>
        conversationService
          .deleteConversation(
            conversationId,
          ),

      onSuccess: async (
        _response,
        deletedConversationId,
      ) => {
        setOpenedMenuId(null)

        if (
          activeConversationId ===
          deletedConversationId
        ) {
          onNewChat()
        }

        await refreshConversations()
      },
    })

  const archiveMutation =
    useMutation({
      mutationFn: (
        conversationId: string,
      ) =>
        conversationService
          .archiveConversation(
            conversationId,
          ),

      onSuccess: async (
        _conversation,
        archivedConversationId,
      ) => {
        setOpenedMenuId(null)

        if (
          activeConversationId ===
          archivedConversationId
        ) {
          onNewChat()
        }

        await refreshConversations()
      },
    })

  const restoreMutation =
    useMutation({
      mutationFn: (
        conversationId: string,
      ) =>
        conversationService
          .restoreConversation(
            conversationId,
          ),

      onSuccess: async () => {
        setOpenedMenuId(null)

        await refreshConversations()
      },
    })

  const conversations =
    conversationsQuery.data
      ?.items ?? []

  const isActionPending =
    renameMutation.isPending ||
    deleteMutation.isPending ||
    archiveMutation.isPending ||
    restoreMutation.isPending

  const startRename = (
    conversation: Conversation,
  ) => {
    setEditingConversationId(
      conversation.id,
    )

    setEditedTitle(
      conversation.title,
    )

    setOpenedMenuId(null)
  }

  const cancelRename = () => {
    setEditingConversationId(null)
    setEditedTitle("")
  }

  const submitRename = (
    conversationId: string,
  ) => {
    const title =
      editedTitle.trim()

    if (!title) {
      return
    }

    renameMutation.mutate({
      conversationId,
      title,
    })
  }

  const handleDelete = (
    conversation: Conversation,
  ) => {
    const confirmed =
      window.confirm(
        `Delete "${conversation.title}"? This action cannot be undone.`,
      )

    if (!confirmed) {
      return
    }

    deleteMutation.mutate(
      conversation.id,
    )
  }

  const handleArchive = (
    conversation: Conversation,
  ) => {
    archiveMutation.mutate(
      conversation.id,
    )
  }

  const handleRestore = (
    conversation: Conversation,
  ) => {
    restoreMutation.mutate(
      conversation.id,
    )
  }

  return (
    <aside
      className={[
        "flex h-full min-h-0 w-full flex-col",
        "border-r bg-background",
        className,
      ].join(" ")}
    >
      <div className="border-b p-3">
        <button
          type="button"
          onClick={onNewChat}
          className={[
            "flex w-full items-center",
            "justify-center gap-2 rounded-md",
            "bg-primary px-4 py-2.5",
            "text-sm font-medium",
            "text-primary-foreground",
            "transition-opacity",
            "hover:opacity-90",
            "focus-visible:outline-none",
            "focus-visible:ring-2",
            "focus-visible:ring-ring",
          ].join(" ")}
        >
          <Plus
            className="h-4 w-4"
            aria-hidden="true"
          />

          New Chat
        </button>
      </div>

      <div className="space-y-3 border-b p-3">
        <div className="relative">
          <Search
            className={[
              "pointer-events-none",
              "absolute left-3 top-1/2",
              "h-4 w-4",
              "-translate-y-1/2",
              "text-muted-foreground",
            ].join(" ")}
            aria-hidden="true"
          />

          <input
            type="search"
            value={searchValue}
            onChange={(event) =>
              setSearchValue(
                event.target.value,
              )
            }
            placeholder="Search chats"
            aria-label="Search conversations"
            className={[
              "h-10 w-full rounded-md",
              "border bg-background",
              "pl-9 pr-9 text-sm",
              "outline-none",
              "placeholder:text-muted-foreground",
              "focus:border-primary",
              "focus:ring-2",
              "focus:ring-primary/20",
            ].join(" ")}
          />

          {searchValue && (
            <button
              type="button"
              onClick={() =>
                setSearchValue("")
              }
              aria-label="Clear search"
              className={[
                "absolute right-2",
                "top-1/2",
                "-translate-y-1/2",
                "rounded p-1",
                "text-muted-foreground",
                "hover:bg-muted",
                "hover:text-foreground",
              ].join(" ")}
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        <div
          className={[
            "grid grid-cols-2",
            "rounded-md bg-muted p-1",
          ].join(" ")}
          role="tablist"
          aria-label="Conversation filters"
        >
          <button
            type="button"
            role="tab"
            aria-selected={
              !showArchived
            }
            onClick={() =>
              setShowArchived(false)
            }
            className={[
              "rounded px-3 py-1.5",
              "text-sm font-medium",
              "transition-colors",
              !showArchived
                ? [
                    "bg-background",
                    "text-foreground",
                    "shadow-sm",
                  ].join(" ")
                : [
                    "text-muted-foreground",
                    "hover:text-foreground",
                  ].join(" "),
            ].join(" ")}
          >
            Chats
          </button>

          <button
            type="button"
            role="tab"
            aria-selected={
              showArchived
            }
            onClick={() =>
              setShowArchived(true)
            }
            className={[
              "rounded px-3 py-1.5",
              "text-sm font-medium",
              "transition-colors",
              showArchived
                ? [
                    "bg-background",
                    "text-foreground",
                    "shadow-sm",
                  ].join(" ")
                : [
                    "text-muted-foreground",
                    "hover:text-foreground",
                  ].join(" "),
            ].join(" ")}
          >
            Archived
          </button>
        </div>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto p-2">
        {conversationsQuery.isLoading && (
          <div
            className={[
              "flex items-center",
              "justify-center gap-2",
              "p-6 text-sm",
              "text-muted-foreground",
            ].join(" ")}
          >
            <Loader2
              className="h-4 w-4 animate-spin"
              aria-hidden="true"
            />

            Loading conversations...
          </div>
        )}

        {conversationsQuery.isError && (
          <div
            className={[
              "space-y-3 rounded-md",
              "border border-destructive/30",
              "bg-destructive/5 p-4",
              "text-sm",
            ].join(" ")}
          >
            <p className="text-destructive">
              Unable to load conversations.
            </p>

            <button
              type="button"
              onClick={() =>
                conversationsQuery
                  .refetch()
              }
              className={[
                "rounded-md border",
                "px-3 py-1.5",
                "font-medium",
                "hover:bg-muted",
              ].join(" ")}
            >
              Try again
            </button>
          </div>
        )}

        {!conversationsQuery.isLoading &&
          !conversationsQuery.isError &&
          conversations.length === 0 && (
            <div
              className={[
                "flex flex-col",
                "items-center",
                "justify-center",
                "px-4 py-10",
                "text-center",
              ].join(" ")}
            >
              <MessageSquare
                className={[
                  "mb-3 h-8 w-8",
                  "text-muted-foreground",
                ].join(" ")}
                aria-hidden="true"
              />

              <p className="text-sm font-medium">
                {showArchived
                  ? "No archived chats"
                  : "No conversations yet"}
              </p>

              <p
                className={[
                  "mt-1 text-xs",
                  "text-muted-foreground",
                ].join(" ")}
              >
                {debouncedSearch
                  ? "No conversations match your search."
                  : showArchived
                    ? "Archived conversations will appear here."
                    : "Start a new chat to create your first conversation."}
              </p>
            </div>
          )}

        <div className="space-y-1">
          {conversations.map(
            (conversation) => {
              const isActive =
                conversation.id ===
                activeConversationId

              const isEditing =
                editingConversationId ===
                conversation.id

              const isMenuOpen =
                openedMenuId ===
                conversation.id

              return (
                <div
                  key={conversation.id}
                  className={[
                    "group relative",
                    "rounded-md border",
                    "transition-colors",
                    isActive
                      ? [
                          "border-primary/30",
                          "bg-primary/10",
                        ].join(" ")
                      : [
                          "border-transparent",
                          "hover:bg-muted/70",
                        ].join(" "),
                  ].join(" ")}
                >
                  {isEditing ? (
                    <div className="flex items-center gap-1 p-2">
                      <input
                        autoFocus
                        value={editedTitle}
                        maxLength={255}
                        onChange={(event) =>
                          setEditedTitle(
                            event.target
                              .value,
                          )
                        }
                        onKeyDown={(
                          event,
                        ) => {
                          if (
                            event.key ===
                            "Enter"
                          ) {
                            submitRename(
                              conversation.id,
                            )
                          }

                          if (
                            event.key ===
                            "Escape"
                          ) {
                            cancelRename()
                          }
                        }}
                        aria-label="Conversation title"
                        className={[
                          "min-w-0 flex-1",
                          "rounded border",
                          "bg-background",
                          "px-2 py-1.5",
                          "text-sm outline-none",
                          "focus:border-primary",
                        ].join(" ")}
                      />

                      <button
                        type="button"
                        onClick={() =>
                          submitRename(
                            conversation.id,
                          )
                        }
                        disabled={
                          !editedTitle.trim() ||
                          renameMutation
                            .isPending
                        }
                        aria-label="Save title"
                        className={[
                          "rounded p-1.5",
                          "hover:bg-muted",
                          "disabled:opacity-50",
                        ].join(" ")}
                      >
                        {renameMutation
                          .isPending ? (
                          <Loader2
                            className={[
                              "h-4 w-4",
                              "animate-spin",
                            ].join(" ")}
                          />
                        ) : (
                          <Check className="h-4 w-4" />
                        )}
                      </button>

                      <button
                        type="button"
                        onClick={
                          cancelRename
                        }
                        disabled={
                          renameMutation
                            .isPending
                        }
                        aria-label="Cancel rename"
                        className={[
                          "rounded p-1.5",
                          "hover:bg-muted",
                          "disabled:opacity-50",
                        ].join(" ")}
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  ) : (
                    <div className="flex items-center">
                      <button
                        type="button"
                        onClick={() =>
                          onSelectConversation(
                            conversation.id,
                          )
                        }
                        className={[
                          "min-w-0 flex-1",
                          "px-3 py-2.5",
                          "text-left",
                          "focus-visible:outline-none",
                          "focus-visible:ring-2",
                          "focus-visible:ring-ring",
                        ].join(" ")}
                      >
                        <div className="flex items-center gap-2">
                          <MessageSquare
                            className={[
                              "h-4 w-4",
                              "shrink-0",
                              isActive
                                ? "text-primary"
                                : "text-muted-foreground",
                            ].join(" ")}
                            aria-hidden="true"
                          />

                          <span
                            className={[
                              "truncate text-sm",
                              isActive
                                ? "font-semibold"
                                : "font-medium",
                            ].join(" ")}
                          >
                            {conversation
                              .title ||
                              "Untitled conversation"}
                          </span>
                        </div>

                        <p
                          className={[
                            "mt-1 truncate",
                            "pl-6 text-xs",
                            "text-muted-foreground",
                          ].join(" ")}
                        >
                          {formatConversationDate(
                            conversation
                              .updated_at ??
                              conversation
                                .created_at,
                          )}
                        </p>
                      </button>

                      <div className="relative pr-1">
                        <button
                          type="button"
                          onClick={() =>
                            setOpenedMenuId(
                              isMenuOpen
                                ? null
                                : conversation.id,
                            )
                          }
                          disabled={
                            isActionPending
                          }
                          aria-label={`Actions for ${conversation.title}`}
                          aria-expanded={
                            isMenuOpen
                          }
                          className={[
                            "rounded p-2",
                            "text-muted-foreground",
                            "opacity-0",
                            "transition-opacity",
                            "hover:bg-muted",
                            "hover:text-foreground",
                            "focus:opacity-100",
                            "group-hover:opacity-100",
                            isMenuOpen
                              ? "opacity-100"
                              : "",
                            "disabled:opacity-50",
                          ].join(" ")}
                        >
                          <MoreHorizontal className="h-4 w-4" />
                        </button>

                        {isMenuOpen && (
                          <div
                            className={[
                              "absolute right-1",
                              "top-10 z-30",
                              "w-40 overflow-hidden",
                              "rounded-md border",
                              "bg-popover p-1",
                              "text-popover-foreground",
                              "shadow-md",
                            ].join(" ")}
                          >
                            {!showArchived && (
                              <button
                                type="button"
                                onClick={() =>
                                  startRename(
                                    conversation,
                                  )
                                }
                                className={[
                                  "flex w-full",
                                  "items-center gap-2",
                                  "rounded px-2",
                                  "py-2 text-sm",
                                  "hover:bg-muted",
                                ].join(" ")}
                              >
                                <Pencil className="h-4 w-4" />
                                Rename
                              </button>
                            )}

                            {showArchived ? (
                              <button
                                type="button"
                                onClick={() =>
                                  handleRestore(
                                    conversation,
                                  )
                                }
                                disabled={
                                  restoreMutation
                                    .isPending
                                }
                                className={[
                                  "flex w-full",
                                  "items-center gap-2",
                                  "rounded px-2",
                                  "py-2 text-sm",
                                  "hover:bg-muted",
                                  "disabled:opacity-50",
                                ].join(" ")}
                              >
                                <RotateCcw className="h-4 w-4" />
                                Restore
                              </button>
                            ) : (
                              <button
                                type="button"
                                onClick={() =>
                                  handleArchive(
                                    conversation,
                                  )
                                }
                                disabled={
                                  archiveMutation
                                    .isPending
                                }
                                className={[
                                  "flex w-full",
                                  "items-center gap-2",
                                  "rounded px-2",
                                  "py-2 text-sm",
                                  "hover:bg-muted",
                                  "disabled:opacity-50",
                                ].join(" ")}
                              >
                                <Archive className="h-4 w-4" />
                                Archive
                              </button>
                            )}

                            <button
                              type="button"
                              onClick={() =>
                                handleDelete(
                                  conversation,
                                )
                              }
                              disabled={
                                deleteMutation
                                  .isPending
                              }
                              className={[
                                "flex w-full",
                                "items-center gap-2",
                                "rounded px-2",
                                "py-2 text-sm",
                                "text-destructive",
                                "hover:bg-destructive/10",
                                "disabled:opacity-50",
                              ].join(" ")}
                            >
                              <Trash2 className="h-4 w-4" />
                              Delete
                            </button>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              )
            },
          )}
        </div>
      </div>
    </aside>
  )
}