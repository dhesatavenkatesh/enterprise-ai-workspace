import {
  CornerDownLeft,
  LoaderCircle,
  Paperclip,
  Send,
  SlidersHorizontal,
  Sparkles,
  Square,
} from "lucide-react"

import {
  useEffect,
  useRef,
  useState,
} from "react"

import {
  Button,
} from "@/components/ui/button"

import {
  cn,
} from "@/lib/utils"

import type {
  LLMProvider,
} from "@/types/chat"

import type {
  PromptTemplate,
} from "@/types/promptTemplate"

interface ChatComposerValues {
  message: string
  provider: LLMProvider
  model_name: string
  temperature: number
  prompt_template_id: string | null
}

interface ChatComposerProps {
  disabled?: boolean
  isGenerating?: boolean
  templates?: PromptTemplate[]
  initialMessage?: string

  onInitialMessageConsumed?: () => void

  onStop?: () => void

  onSend: (
    values: ChatComposerValues,
  ) =>
    | Promise<boolean>
    | boolean
    | Promise<void>
    | void
}

const MAX_MESSAGE_LENGTH = 4000

const providerModels: Record<
  LLMProvider,
  string[]
> = {
  groq: [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "openai/gpt-oss-120b",
  ],

  openai: [
    "gpt-4.1-mini",
    "gpt-4.1",
  ],

  ollama: [
    "llama3.2",
    "mistral",
  ],
}

export function ChatComposer({
  disabled = false,
  isGenerating = false,
  templates = [],
  initialMessage = "",
  onInitialMessageConsumed,
  onStop,
  onSend,
}: ChatComposerProps) {
  const textareaRef =
    useRef<HTMLTextAreaElement | null>(
      null,
    )

  const [message, setMessage] =
    useState("")

  const [provider, setProvider] =
    useState<LLMProvider>("groq")

  const [modelName, setModelName] =
    useState(
      providerModels.groq[0],
    )

  const [
    selectedTemplateId,
    setSelectedTemplateId,
  ] = useState("")

  const [temperature, setTemperature] =
    useState(0.7)

  const [
    showAdvanced,
    setShowAdvanced,
  ] = useState(false)

  const inputDisabled =
    disabled || isGenerating

  const characterCount =
    message.length

  const isAtLimit =
    characterCount >=
    MAX_MESSAGE_LENGTH

  const isNearLimit =
    characterCount >=
    MAX_MESSAGE_LENGTH * 0.9

  const resizeTextarea = (): void => {
    const textarea =
      textareaRef.current

    if (!textarea) {
      return
    }

    textarea.style.height = "auto"

    textarea.style.height =
      `${Math.min(
        textarea.scrollHeight,
        180,
      )}px`
  }

  useEffect(() => {
    if (!initialMessage) {
      return
    }

    setMessage(
      initialMessage.slice(
        0,
        MAX_MESSAGE_LENGTH,
      ),
    )

    window.setTimeout(() => {
      resizeTextarea()
      textareaRef.current?.focus()
    }, 0)

    onInitialMessageConsumed?.()
  }, [
    initialMessage,
    onInitialMessageConsumed,
  ])

  useEffect(() => {
    const availableModels =
      providerModels[provider]

    if (
      !availableModels.includes(
        modelName,
      )
    ) {
      setModelName(
        availableModels[0],
      )
    }
  }, [
    modelName,
    provider,
  ])

  const handleSubmit =
    async (): Promise<void> => {
      const trimmedMessage =
        message.trim()

      if (
        !trimmedMessage ||
        inputDisabled ||
        trimmedMessage.length >
          MAX_MESSAGE_LENGTH
      ) {
        return
      }

      const result =
        await onSend({
          message: trimmedMessage,
          provider,
          model_name: modelName,
          temperature,
          prompt_template_id:
            selectedTemplateId ||
            null,
        })

      /*
       * AIChatPage returns false when the
       * request is stopped or fails.
       * Keep the text in the composer in
       * those cases so the user can retry.
       */
      if (result === false) {
        textareaRef.current?.focus()
        return
      }

      setMessage("")

      if (textareaRef.current) {
        textareaRef.current.style.height =
          "auto"

        textareaRef.current.focus()
      }
    }

  const handleKeyDown = (
    event:
      React.KeyboardEvent<HTMLTextAreaElement>,
  ): void => {
    if (
      event.key === "Enter" &&
      !event.shiftKey
    ) {
      event.preventDefault()

      if (!inputDisabled) {
        void handleSubmit()
      }
    }
  }

  return (
    <section className="border-t bg-background/95 p-3 backdrop-blur md:p-4">
      <div className="mx-auto max-w-4xl">
        {showAdvanced && (
          <div className="mb-3 grid gap-3 rounded-xl border bg-muted/30 p-3 sm:grid-cols-2 lg:grid-cols-4">
            <label className="space-y-1.5">
              <span className="text-xs font-medium text-muted-foreground">
                Provider
              </span>

              <select
                value={provider}
                disabled={inputDisabled}
                onChange={(event) => {
                  setProvider(
                    event.target
                      .value as LLMProvider,
                  )
                }}
                className="h-9 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <option value="groq">
                  Groq
                </option>

                <option value="openai">
                  OpenAI
                </option>

                <option value="ollama">
                  Ollama
                </option>
              </select>
            </label>

            <label className="space-y-1.5">
              <span className="text-xs font-medium text-muted-foreground">
                Model
              </span>

              <select
                value={modelName}
                disabled={inputDisabled}
                onChange={(event) => {
                  setModelName(
                    event.target.value,
                  )
                }}
                className="h-9 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 disabled:cursor-not-allowed disabled:opacity-60"
              >
                {providerModels[
                  provider
                ].map((model) => (
                  <option
                    key={model}
                    value={model}
                  >
                    {model}
                  </option>
                ))}
              </select>
            </label>

            <label className="space-y-1.5">
              <span className="text-xs font-medium text-muted-foreground">
                Prompt template
              </span>

              <select
                value={
                  selectedTemplateId
                }
                disabled={inputDisabled}
                onChange={(event) => {
                  setSelectedTemplateId(
                    event.target.value,
                  )
                }}
                className="h-9 w-full rounded-lg border bg-background px-3 text-sm outline-none focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20 disabled:cursor-not-allowed disabled:opacity-60"
              >
                <option value="">
                  No template
                </option>

                {templates.map(
                  (template) => (
                    <option
                      key={template.id}
                      value={template.id}
                    >
                      {template.name}
                    </option>
                  ),
                )}
              </select>
            </label>

            <label className="space-y-1.5">
              <span className="flex items-center justify-between text-xs font-medium text-muted-foreground">
                <span>
                  Temperature
                </span>

                <span>
                  {temperature.toFixed(
                    1,
                  )}
                </span>
              </span>

              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={temperature}
                disabled={inputDisabled}
                onChange={(event) => {
                  setTemperature(
                    Number(
                      event.target.value,
                    ),
                  )
                }}
                className="h-9 w-full accent-violet-600 disabled:cursor-not-allowed disabled:opacity-60"
              />
            </label>
          </div>
        )}

        <div
          className={cn(
            "rounded-2xl border bg-card p-2 shadow-sm transition",
            "focus-within:border-violet-500 focus-within:ring-4 focus-within:ring-violet-500/10",
            inputDisabled &&
              "bg-muted/20",
          )}
        >
          <textarea
            ref={textareaRef}
            rows={1}
            value={message}
            disabled={inputDisabled}
            maxLength={
              MAX_MESSAGE_LENGTH
            }
            placeholder={
              isGenerating
                ? "AI is generating a response..."
                : "Ask Enterprise AI anything..."
            }
            onInput={resizeTextarea}
            onChange={(event) => {
              const value =
                event.target.value.slice(
                  0,
                  MAX_MESSAGE_LENGTH,
                )

              setMessage(value)
            }}
            onKeyDown={handleKeyDown}
            className="max-h-45 min-h-12 w-full resize-none bg-transparent px-3 py-2.5 text-sm leading-6 outline-none placeholder:text-muted-foreground disabled:cursor-not-allowed"
          />

          <div className="flex items-center justify-between px-3 pb-1">
            <span className="text-xs text-muted-foreground">
              Shift + Enter for a new line
            </span>

            <span
              className={cn(
                "text-xs tabular-nums",
                isAtLimit &&
                  "font-medium text-destructive",
                !isAtLimit &&
                  isNearLimit &&
                  "font-medium text-amber-600 dark:text-amber-400",
                !isNearLimit &&
                  "text-muted-foreground",
              )}
            >
              {characterCount}/
              {MAX_MESSAGE_LENGTH}
            </span>
          </div>

          <div className="flex items-center justify-between gap-3 px-1 pb-1 pt-1">
            <div className="flex items-center gap-1">
              <Button
                type="button"
                size="icon"
                variant="ghost"
                disabled
                aria-label="Attach file"
                title="File attachments will be added later"
              >
                <Paperclip className="h-4 w-4" />
              </Button>

              <Button
                type="button"
                variant={
                  showAdvanced
                    ? "secondary"
                    : "ghost"
                }
                size="sm"
                disabled={inputDisabled}
                onClick={() => {
                  setShowAdvanced(
                    (current) =>
                      !current,
                  )
                }}
              >
                <SlidersHorizontal className="h-4 w-4" />
                Options
              </Button>

              {selectedTemplateId && (
                <span className="hidden items-center gap-1 rounded-full bg-violet-50 px-2.5 py-1 text-xs font-medium text-violet-700 sm:flex dark:bg-violet-950/40 dark:text-violet-300">
                  <Sparkles className="h-3 w-3" />
                  Template selected
                </span>
              )}
            </div>

            <div className="flex items-center gap-3">
              <span className="hidden items-center gap-1 text-xs text-muted-foreground md:flex">
                <CornerDownLeft className="h-3 w-3" />
                Enter to send
              </span>

              {isGenerating ? (
                <Button
                  type="button"
                  size="icon-lg"
                  aria-label="Stop generation"
                  title="Stop generation"
                  onClick={onStop}
                  className="rounded-xl bg-destructive text-destructive-foreground hover:bg-destructive/90"
                >
                  <Square className="h-4 w-4 fill-current" />
                </Button>
              ) : (
                <Button
                  type="button"
                  size="icon-lg"
                  aria-label="Send message"
                  title="Send message"
                  disabled={
                    disabled ||
                    !message.trim() ||
                    characterCount >
                      MAX_MESSAGE_LENGTH
                  }
                  onClick={() => {
                    void handleSubmit()
                  }}
                  className="rounded-xl bg-violet-600 text-white hover:bg-violet-700"
                >
                  {disabled ? (
                    <LoaderCircle className="h-5 w-5 animate-spin" />
                  ) : (
                    <Send className="h-5 w-5" />
                  )}
                </Button>
              )}
            </div>
          </div>
        </div>

        <p className="mt-2 text-center text-xs text-muted-foreground">
          AI responses may contain mistakes.
          Verify important enterprise
          information.
        </p>
      </div>
    </section>
  )
}