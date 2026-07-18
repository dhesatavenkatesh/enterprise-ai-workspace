import {
  Bot,
  Check,
  Copy,
  User,
} from "lucide-react"

import {
  useState,
} from "react"

import {
  Button,
} from "@/components/ui/button"

import {
  cn,
} from "@/lib/utils"

import type {
  ChatMessage as ChatMessageType,
} from "@/types/chat"

interface ChatMessageProps {
  message: ChatMessageType
}

function formatMessageTime(
  value: string,
): string {
  const date = new Date(value)

  if (
    Number.isNaN(
      date.getTime(),
    )
  ) {
    return ""
  }

  return new Intl.DateTimeFormat(
    undefined,
    {
      hour: "2-digit",
      minute: "2-digit",
    },
  ).format(date)
}

export function ChatMessage({
  message,
}: ChatMessageProps) {
  const [copied, setCopied] =
    useState(false)

  const isUser =
    message.role === "user"

  const handleCopy = async (): Promise<void> => {
    try {
      await navigator.clipboard.writeText(
        message.content,
      )

      setCopied(true)

      window.setTimeout(() => {
        setCopied(false)
      }, 1500)
    } catch {
      setCopied(false)
    }
  }

  return (
    <article
      className={cn(
        "group flex w-full gap-3",
        isUser
          ? "justify-end"
          : "justify-start",
      )}
    >
      {!isUser && (
        <div className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-indigo-600 text-white shadow-sm">
          <Bot className="h-5 w-5" />
        </div>
      )}

      <div
        className={cn(
          "max-w-[85%] md:max-w-[75%]",
          isUser
            ? "items-end"
            : "items-start",
        )}
      >
        <div
          className={cn(
            "rounded-2xl px-4 py-3 shadow-sm",
            isUser
              ? "rounded-br-md bg-violet-600 text-white"
              : "rounded-bl-md border bg-card text-card-foreground",
          )}
        >
          <div className="whitespace-pre-wrap break-words text-sm leading-6">
            {message.content}
          </div>
        </div>

        <div
          className={cn(
            "mt-1.5 flex min-h-7 items-center gap-2 px-1 text-xs text-muted-foreground",
            isUser
              ? "justify-end"
              : "justify-start",
          )}
        >
          <span>
            {formatMessageTime(
              message.created_at,
            )}
          </span>

          {!isUser &&
            message.model_name && (
              <>
                <span>•</span>

                <span>
                  {message.model_name}
                </span>
              </>
            )}

          {!isUser &&
            message.token_count > 0 && (
              <>
                <span>•</span>

                <span>
                  {message.token_count} tokens
                </span>
              </>
            )}

          <Button
            type="button"
            variant="ghost"
            size="icon-xs"
            aria-label="Copy message"
            title="Copy message"
            onClick={() => {
              void handleCopy()
            }}
            className="opacity-0 transition-opacity group-hover:opacity-100"
          >
            {copied ? (
              <Check className="h-3.5 w-3.5 text-emerald-600" />
            ) : (
              <Copy className="h-3.5 w-3.5" />
            )}
          </Button>
        </div>
      </div>

      {isUser && (
        <div className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-slate-900 text-white shadow-sm">
          <User className="h-5 w-5" />
        </div>
      )}
    </article>
  )
}