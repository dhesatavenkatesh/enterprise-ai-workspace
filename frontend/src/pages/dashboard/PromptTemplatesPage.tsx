import {
  FileText,
  LoaderCircle,
  Plus,
  Search,
  X,
} from "lucide-react"
import {
  useMemo,
  useState,
} from "react"

import {
  PromptTemplateCard,
} from "@/components/prompts/PromptTemplateCard"
import {
  PromptTemplateForm,
} from "@/components/prompts/PromptTemplateForm"
import { Button } from "@/components/ui/button"
import {
  useCreatePromptTemplate,
  useDeletePromptTemplate,
  usePromptTemplates,
  useUpdatePromptTemplate,
} from "@/hooks/usePromptTemplates"
import { getApiError } from "@/utils/getApiError"

import type {
  CreatePromptTemplateRequest,
  PromptTemplate,
} from "@/types/promptTemplate"

export function PromptTemplatesPage() {
  const [search, setSearch] =
    useState("")
  const [category, setCategory] =
    useState("")
  const [formOpen, setFormOpen] =
    useState(false)
  const [
    selectedTemplate,
    setSelectedTemplate,
  ] =
    useState<PromptTemplate | null>(
      null,
    )
  const [error, setError] =
    useState("")

  const templatesQuery =
    usePromptTemplates({
      page: 1,
      page_size: 100,
    })

  const createTemplate =
    useCreatePromptTemplate()
  const updateTemplate =
    useUpdatePromptTemplate()
  const deleteTemplate =
    useDeletePromptTemplate()

  const templates =
    templatesQuery.data?.items ?? []

  const categories = useMemo<string[]>(() => {
  return Array.from(
    new Set(
      templates
        .map((template) => template.category)
        .filter(
          (categoryName): categoryName is string =>
            Boolean(categoryName),
        ),
    ),
  ).sort()
}, [templates])

  const filteredTemplates =
    useMemo(() => {
      const normalizedSearch =
        search.trim().toLowerCase()

      return templates.filter(
        (template) => {
          const matchesSearch =
            !normalizedSearch ||
            template.name
              .toLowerCase()
              .includes(
                normalizedSearch,
              ) ||
            template.content
              .toLowerCase()
              .includes(
                normalizedSearch,
              ) ||
            template.description
              ?.toLowerCase()
              .includes(
                normalizedSearch,
              )

          const matchesCategory =
            !category ||
            template.category ===
              category

          return (
            matchesSearch &&
            matchesCategory
          )
        },
      )
    }, [
      category,
      search,
      templates,
    ])

  const openCreateForm = (): void => {
    setSelectedTemplate(null)
    setError("")
    setFormOpen(true)
  }

  const openEditForm = (
    template: PromptTemplate,
  ): void => {
    setSelectedTemplate(template)
    setError("")
    setFormOpen(true)
  }

  const closeForm = (): void => {
    if (
      createTemplate.isPending ||
      updateTemplate.isPending
    ) {
      return
    }

    setSelectedTemplate(null)
    setError("")
    setFormOpen(false)
  }

  const handleSubmit =
    async (
      values: CreatePromptTemplateRequest,
    ): Promise<void> => {
      setError("")

      try {
        if (selectedTemplate) {
          await updateTemplate.mutateAsync({
            templateId:
              selectedTemplate.id,
            payload: values,
          })
        } else {
          await createTemplate.mutateAsync(
            values,
          )
        }

        closeForm()
      } catch (submitError) {
        setError(
          getApiError(
            submitError,
            selectedTemplate
              ? "Unable to update the prompt template."
              : "Unable to create the prompt template.",
          ),
        )
      }
    }

  const handleDelete =
    async (
      template: PromptTemplate,
    ): Promise<void> => {
      const confirmed =
        window.confirm(
          `Delete the template "${template.name}"?`,
        )

      if (!confirmed) {
        return
      }

      setError("")

      try {
        await deleteTemplate.mutateAsync(
          template.id,
        )
      } catch (deleteError) {
        setError(
          getApiError(
            deleteError,
            "Unable to delete the prompt template.",
          ),
        )
      }
    }

  const isSubmitting =
    createTemplate.isPending ||
    updateTemplate.isPending

  return (
    <div className="space-y-6">
      <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">
            Prompt Templates
          </h1>

          <p className="mt-1 text-sm text-muted-foreground">
            Create reusable prompts for
            common enterprise AI tasks.
          </p>
        </div>

        <Button
          type="button"
          onClick={openCreateForm}
          className="bg-violet-600 text-white hover:bg-violet-700"
        >
          <Plus className="h-4 w-4" />
          New template
        </Button>
      </div>

      <section className="grid gap-4 rounded-2xl border bg-card p-4 sm:grid-cols-[1fr_220px]">
        <div className="relative">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />

          <input
            type="search"
            value={search}
            placeholder="Search templates..."
            onChange={(event) => {
              setSearch(
                event.target.value,
              )
            }}
            className="h-10 w-full rounded-lg border bg-background pl-9 pr-3 text-sm outline-none transition focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20"
          />
        </div>

        <select
          value={category}
          onChange={(event) => {
            setCategory(
              event.target.value,
            )
          }}
          className="h-10 rounded-lg border bg-background px-3 text-sm outline-none transition focus:border-violet-500 focus:ring-2 focus:ring-violet-500/20"
        >
          <option value="">
            All categories
          </option>

          {categories.map(
            (categoryName) => (
              <option
                key={categoryName}
                value={categoryName}
              >
                {categoryName}
              </option>
            ),
          )}
        </select>
      </section>

      {error && (
        <div className="rounded-xl border border-destructive/20 bg-destructive/10 px-4 py-3 text-sm text-destructive">
          {error}
        </div>
      )}

      {templatesQuery.isLoading && (
        <div className="flex h-64 items-center justify-center rounded-2xl border bg-card">
          <div className="text-center">
            <LoaderCircle className="mx-auto h-7 w-7 animate-spin text-violet-600" />

            <p className="mt-3 text-sm text-muted-foreground">
              Loading prompt templates...
            </p>
          </div>
        </div>
      )}

      {templatesQuery.isError && (
        <div className="rounded-2xl border border-destructive/20 bg-destructive/10 p-6 text-center">
          <p className="font-medium text-destructive">
            Prompt templates could not be
            loaded.
          </p>

          <Button
            type="button"
            variant="outline"
            className="mt-4"
            onClick={() => {
              void templatesQuery.refetch()
            }}
          >
            Try again
          </Button>
        </div>
      )}

      {!templatesQuery.isLoading &&
        !templatesQuery.isError &&
        filteredTemplates.length ===
          0 && (
          <div className="flex min-h-72 flex-col items-center justify-center rounded-2xl border border-dashed bg-card px-6 text-center">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-violet-100 text-violet-700 dark:bg-violet-950/40 dark:text-violet-300">
              <FileText className="h-7 w-7" />
            </div>

            <h2 className="mt-4 text-lg font-semibold">
              No prompt templates found
            </h2>

            <p className="mt-2 max-w-md text-sm leading-6 text-muted-foreground">
              Create a reusable prompt template
              or change the current search
              filters.
            </p>

            <Button
              type="button"
              className="mt-5 bg-violet-600 text-white hover:bg-violet-700"
              onClick={openCreateForm}
            >
              <Plus className="h-4 w-4" />
              Create template
            </Button>
          </div>
        )}

      {!templatesQuery.isLoading &&
        !templatesQuery.isError &&
        filteredTemplates.length >
          0 && (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {filteredTemplates.map(
              (template) => (
                <PromptTemplateCard
                  key={template.id}
                  template={template}
                  deleting={
                    deleteTemplate.isPending
                  }
                  onEdit={openEditForm}
                  onDelete={(item) => {
                    void handleDelete(
                      item,
                    )
                  }}
                />
              ),
            )}
          </div>
        )}

      {formOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
          <div
            role="dialog"
            aria-modal="true"
            aria-labelledby="prompt-template-dialog-title"
            className="max-h-[92vh] w-full max-w-2xl overflow-y-auto rounded-2xl border bg-background shadow-2xl"
          >
            <div className="flex items-center justify-between border-b px-5 py-4">
              <div>
                <h2
                  id="prompt-template-dialog-title"
                  className="text-lg font-semibold"
                >
                  {selectedTemplate
                    ? "Edit prompt template"
                    : "Create prompt template"}
                </h2>

                <p className="mt-1 text-xs text-muted-foreground">
                  Configure a reusable prompt
                  for the AI assistant.
                </p>
              </div>

              <Button
                type="button"
                variant="ghost"
                size="icon"
                disabled={isSubmitting}
                aria-label="Close dialog"
                onClick={closeForm}
              >
                <X className="h-5 w-5" />
              </Button>
            </div>

            <div className="p-5">
              <PromptTemplateForm
                template={
                  selectedTemplate
                }
                isSubmitting={
                  isSubmitting
                }
                onSubmit={handleSubmit}
                onCancel={closeForm}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default PromptTemplatesPage