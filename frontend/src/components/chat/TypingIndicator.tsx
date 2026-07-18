import {
  Bot,
} from "lucide-react"

export function TypingIndicator() {
  return (
    <div className="flex items-start gap-3">
      <div className="mt-1 flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-indigo-600 text-white shadow-sm">
        <Bot className="h-5 w-5" />
      </div>

      <div className="rounded-2xl rounded-bl-md border bg-card px-4 py-4 shadow-sm">
        <div className="flex items-center gap-1.5">
          <span className="h-2 w-2 animate-bounce rounded-full bg-violet-500 [animation-delay:-0.3s]" />

          <span className="h-2 w-2 animate-bounce rounded-full bg-violet-500 [animation-delay:-0.15s]" />

          <span className="h-2 w-2 animate-bounce rounded-full bg-violet-500" />
        </div>
      </div>
    </div>
  )
}