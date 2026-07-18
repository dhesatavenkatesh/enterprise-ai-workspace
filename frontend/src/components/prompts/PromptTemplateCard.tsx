import {
  Copy,
  Edit3,
  FileText,
  MoreVertical,
  Trash2,
} from "lucide-react"
import { useState } from "react"

import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"

import type {
  PromptTemplate,
} from "@/types/promptTemplate"

interface PromptTemplateCardProps {
  template: PromptTemplate
  deleting?: boolean
  onEdit: (
    template: PromptTemplate,
  ) => void
  onDelete: (
    template: PromptTemplate,
  ) => void
}

export function PromptTemplateCard({
  template,
  deleting = false,
  onEdit,
  onDelete,
}: PromptTemplateCardProps) {
  const [copied, setCopied] =
    useState(false)

  const handleCopy =
    async (): Promise<void> => {
      try {
        await navigator.clipboard.writeText(
          template.content,
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
    <article className="group flex h-full flex-col rounded-2xl border bg-card p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md">
      <div className="flex items-start justify-between gap-3">
        <div className="flex min-w-0 items-start gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-violet-100 text-violet-700 dark:bg-violet-950/40 dark:text-violet-300">
            <FileText className="h-5 w-5" />
          </div>

          <div className="min-w-0">
            <h3 className="truncate font-semibold">
              {template.name}
            </h3>

            <div className="mt-1 flex flex-wrap items-center gap-2">
              <span className="rounded-full bg-muted px-2 py-0.5 text-xs text-muted-foreground">
                {template.category ||
                  "general"}
              </span>

              <span
                className={cn(
                  "rounded-full px-2 py-0.5 text-xs font-medium",
                  template.status ===
                    "active"
                    ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300"
                    : "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300",
                )}
              >
                {template.status}
              </span>
            </div>
          </div>
        </div>

        <MoreVertical className="h-4 w-4 shrink-0 text-muted-foreground" />
      </div>

      {template.description && (
        <p className="mt-4 line-clamp-2 text-sm leading-6 text-muted-foreground">
          {template.description}
        </p>
      )}

      <div className="mt-4 flex-1 rounded-xl bg-muted/50 p-3">
        <p className="line-clamp-5 whitespace-pre-wrap text-sm leading-6">
          {template.content}
        </p>
      </div>

      <div className="mt-4 flex items-center justify-between border-t pt-4">
        <div className="text-xs text-muted-foreground">
          Used {template.usage_count ?? 0}
          {" "}
          times
        </div>

        <div className="flex items-center gap-1">
          <Button
            type="button"
            variant="ghost"
            size="icon"
            title="Copy prompt"
            aria-label="Copy prompt"
            onClick={() => {
              void handleCopy()
            }}
          >
            <Copy className="h-4 w-4" />
          </Button>

          <Button
            type="button"
            variant="ghost"
            size="icon"
            title="Edit template"
            aria-label="Edit template"
            onClick={() => {
              onEdit(template)
            }}
          >
            <Edit3 className="h-4 w-4" />
          </Button>

          <Button
            type="button"
            variant="ghost"
            size="icon"
            disabled={deleting}
            title="Delete template"
            aria-label="Delete template"
            onClick={() => {
              onDelete(template)
            }}
            className="hover:text-destructive"
          >
            <Trash2 className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {copied && (
        <p className="mt-2 text-right text-xs font-medium text-emerald-600">
          Prompt copied
        </p>
      )}
    </article>
  )
}