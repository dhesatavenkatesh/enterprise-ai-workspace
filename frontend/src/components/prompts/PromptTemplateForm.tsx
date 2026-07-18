import { LoaderCircle, Save, X } from "lucide-react"
import { useEffect, useState } from "react"

import { Button } from "@/components/ui/button"

import type {
  CreatePromptTemplateRequest,
  PromptTemplate,
  PromptTemplateStatus,
} from "@/types/promptTemplate"

interface PromptTemplateFormProps {
  template?: PromptTemplate | null
  isSubmitting?: boolean
  onSubmit: (
    values: CreatePromptTemplateRequest,
  ) => Promise<void> | void
  onCancel: () => void
}

export function PromptTemplateForm({
  template = null,
  isSubmitting = false,
  onSubmit,
  onCancel,
}: PromptTemplateFormProps) {
  const [name, setName] = useState("")
  const [description, setDescription] =
    useState("")
  const [content, setContent] = useState("")
  const [category, setCategory] =
    useState("general")
  const [status, setStatus] =
  useState<PromptTemplateStatus>("active")
  const [error, setError] = useState("")

  useEffect(() => {
    if (!template) {
      setName("")
      setDescription("")
      setContent("")
      setCategory("general")
      setStatus("active")
      setError("")
      return
    }

    setName(template.name)
    setDescription(template.description ?? "")
    setContent(template.content)
    setCategory(template.category ?? "general")
    setStatus(template.status)
    setError("")
  }, [template])

  const handleSubmit = async (
    event: React.FormEvent<HTMLFormElement>,
  ): Promise<void> => {
    event.preventDefault()

    const trimmedName = name.trim()
    const trimmedContent = content.trim()

    if (!trimmedName) {
      setError("Template name is required.")
      return
    }

    if (!trimmedContent) {
      setError("Prompt content is required.")
      return
    }

    setError("")

    await onSubmit({
      name: trimmedName,
      description:
        description.trim() || null,
      content: trimmedContent,
      category:
        category.trim() || "general",
      status,
    })
  }

  return (
    <form
      onSubmit={(event) => {
        void handleSubmit(event)
      }}
      className="space-y-5"
    >
      <div>
        <label
          htmlFor="template-name"
          className="mb-1.5 block text-sm font-medium"
        >
          Template name
        </label>

        <input
          id="template-name"
          type="text"
          value={name}
          disabled={isSubmitting}
          placeholder="Example: Project status update"
          onChange={(event) => {
            setName(event.target.value)
          }}
          className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none transition focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20"
        />
      </div>

      <div>
        <label
          htmlFor="template-description"
          className="mb-1.5 block text-sm font-medium"
        >
          Description
        </label>

        <input
          id="template-description"
          type="text"
          value={description}
          disabled={isSubmitting}
          placeholder="Explain when this prompt should be used"
          onChange={(event) => {
            setDescription(event.target.value)
          }}
          className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none transition focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20"
        />
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label
            htmlFor="template-category"
            className="mb-1.5 block text-sm font-medium"
          >
            Category
          </label>

          <input
            id="template-category"
            type="text"
            value={category}
            disabled={isSubmitting}
            placeholder="general"
            onChange={(event) => {
              setCategory(event.target.value)
            }}
            className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none transition focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20"
          />
        </div>

        <div>
          <label
            htmlFor="template-status"
            className="mb-1.5 block text-sm font-medium"
          >
            Status
          </label>

          <select
            id="template-status"
            value={status}
            disabled={isSubmitting}
            onChange={(event) => {
  setStatus(
    event.target.value as PromptTemplateStatus,
  )
}}
            className="h-10 w-full rounded-lg border bg-background px-3 text-sm outline-none transition focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20"
          >
            <option value="active">
              Active
            </option>

            <option value="inactive">
              Inactive
            </option>
          </select>
        </div>
      </div>

      <div>
        <label
          htmlFor="template-content"
          className="mb-1.5 block text-sm font-medium"
        >
          Prompt content
        </label>

        <textarea
          id="template-content"
          rows={9}
          value={content}
          disabled={isSubmitting}
          placeholder="Write the reusable prompt instructions here..."
          onChange={(event) => {
            setContent(event.target.value)
          }}
          className="w-full resize-y rounded-lg border bg-background px-3 py-3 text-sm leading-6 outline-none transition focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20"
        />

        <p className="mt-1 text-xs text-muted-foreground">
          You can add placeholders such as
          {" "}
          <code>{"{project_name}"}</code>
          {" "}
          or
          {" "}
          <code>{"{topic}"}</code>.
        </p>
      </div>

      {error && (
        <div className="rounded-lg border border-destructive/20 bg-destructive/10 px-3 py-2 text-sm text-destructive">
          {error}
        </div>
      )}

      <div className="flex justify-end gap-2 border-t pt-4">
        <Button
          type="button"
          variant="outline"
          disabled={isSubmitting}
          onClick={onCancel}
        >
          <X className="h-4 w-4" />
          Cancel
        </Button>

        <Button
          type="submit"
          disabled={isSubmitting}
          className="bg-violet-600 text-white hover:bg-violet-700"
        >
          {isSubmitting ? (
            <LoaderCircle className="h-4 w-4 animate-spin" />
          ) : (
            <Save className="h-4 w-4" />
          )}

          {template
            ? "Update template"
            : "Create template"}
        </Button>
      </div>
    </form>
  )
}
