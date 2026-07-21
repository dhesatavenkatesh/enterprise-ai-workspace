import {
  CheckCircle2,
  Database,
  File,
  FileText,
  LoaderCircle,
  Search,
  Trash2,
  Upload,
  X,
} from "lucide-react"

import {
  type ChangeEvent,
  type DragEvent,
  useMemo,
  useRef,
  useState,
} from "react"

import { toast } from "sonner"

import {
  Button,
} from "@/components/ui/button"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

import {
  Input,
} from "@/components/ui/input"

import {
  useDeleteDocument,
  useDocuments,
  useIndexDocument,
  useUploadDocument,
} from "@/hooks/useDocuments"

import type {
  KnowledgeDocument,
} from "@/types/document"

const departments = [
  "All",
  "General",
  "HR",
  "Engineering",
  "Projects",
  "Finance",
  "Legal",
  "Operations",
]

const supportedExtensions = [
  ".pdf",
  ".docx",
  ".txt",
  ".md",
  ".markdown",
]

const maxFileSize =
  20 * 1024 * 1024

function getExtension(
  fileName: string,
): string {
  const dotIndex =
    fileName.lastIndexOf(".")

  if (dotIndex === -1) {
    return ""
  }

  return fileName
    .slice(dotIndex)
    .toLowerCase()
}

function getDocumentType(
  fileName: string,
): string {
  return getExtension(fileName)
    .replace(".", "")
}

function formatBytes(
  bytes: number,
): string {
  if (bytes === 0) {
    return "0 B"
  }

  const units = [
    "B",
    "KB",
    "MB",
    "GB",
  ]

  const index = Math.min(
    Math.floor(
      Math.log(bytes) /
        Math.log(1024),
    ),
    units.length - 1,
  )

  const value =
    bytes /
    1024 ** index

  return `${value.toFixed(
    index === 0 ? 0 : 1,
  )} ${units[index]}`
}

function getStatusStyle(
  status: string,
): string {
  switch (
    status.toLowerCase()
  ) {
    case "completed":
    case "indexed":
      return "bg-emerald-100 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300"

    case "processing":
      return "bg-blue-100 text-blue-700 dark:bg-blue-950/40 dark:text-blue-300"

    case "failed":
      return "bg-red-100 text-red-700 dark:bg-red-950/40 dark:text-red-300"

    default:
      return "bg-amber-100 text-amber-700 dark:bg-amber-950/40 dark:text-amber-300"
  }
}

function isIndexed(
  status: string,
): boolean {
  return (
    status === "completed" ||
    status === "indexed"
  )
}

export function KnowledgeBasePage() {
  const fileInputRef =
    useRef<HTMLInputElement | null>(
      null,
    )

  const [
    search,
    setSearch,
  ] = useState("")

  const [
    department,
    setDepartment,
  ] = useState("All")

  const [
    uploadDepartment,
    setUploadDepartment,
  ] = useState("General")

  const [
    selectedFiles,
    setSelectedFiles,
  ] = useState<File[]>([])

  const [
    selectedDocument,
    setSelectedDocument,
  ] =
    useState<KnowledgeDocument | null>(
      null,
    )

  const [
    isDragging,
    setIsDragging,
  ] = useState(false)

  const documentsQuery =
    useDocuments({
      page: 1,
      page_size: 100,
      search:
        search.trim() || undefined,
      department:
        department === "All"
          ? undefined
          : department,
    })

  const uploadMutation =
    useUploadDocument()

  const indexMutation =
    useIndexDocument()

  const deleteMutation =
    useDeleteDocument()

  const documents =
    documentsQuery.data?.items ?? []

  const statistics = useMemo(() => {
    const processing =
      documents.filter(
        (document) =>
          document.status ===
            "processing" ||
          document.status ===
            "uploaded",
      ).length

    const indexed =
      documents.filter(
        (document) =>
          isIndexed(
            document.status,
          ),
      ).length

    const storage =
      documents.reduce(
        (
          total,
          document,
        ) =>
          total +
          document.file_size,
        0,
      )

    return {
      total:
        documentsQuery.data?.total ??
        documents.length,

      processing,
      indexed,
      storage,
    }
  }, [
    documents,
    documentsQuery.data?.total,
  ])

  const validateFiles = (
    files: File[],
  ): File[] => {
    return files.filter(
      (file) => {
        const extension =
          getExtension(file.name)

        if (
          !supportedExtensions.includes(
            extension,
          )
        ) {
          toast.error(
            `${file.name}: unsupported format`,
          )

          return false
        }

        if (
          file.size >
          maxFileSize
        ) {
          toast.error(
            `${file.name}: maximum size is 20 MB`,
          )

          return false
        }

        return true
      },
    )
  }

  const addFiles = (
    files: File[],
  ): void => {
    const validFiles =
      validateFiles(files)

    setSelectedFiles(
      (currentFiles) => {
        const existingFiles =
          new Set(
            currentFiles.map(
              (file) =>
                `${file.name}-${file.size}`,
            ),
          )

        const uniqueFiles =
          validFiles.filter(
            (file) =>
              !existingFiles.has(
                `${file.name}-${file.size}`,
              ),
          )

        return [
          ...currentFiles,
          ...uniqueFiles,
        ]
      },
    )
  }

  const handleFileChange = (
    event:
      ChangeEvent<HTMLInputElement>,
  ): void => {
    const files =
      Array.from(
        event.target.files ?? [],
      )

    addFiles(files)

    event.target.value = ""
  }

  const handleDrop = (
    event:
      DragEvent<HTMLDivElement>,
  ): void => {
    event.preventDefault()

    setIsDragging(false)

    addFiles(
      Array.from(
        event.dataTransfer.files,
      ),
    )
  }

  const removeFile = (
    selectedFile: File,
  ): void => {
    setSelectedFiles(
      (currentFiles) =>
        currentFiles.filter(
          (file) =>
            !(
              file.name ===
                selectedFile.name &&
              file.size ===
                selectedFile.size
            ),
        ),
    )
  }

  const handleUpload =
    async (): Promise<void> => {
      if (
        selectedFiles.length === 0
      ) {
        toast.error(
          "Select at least one file",
        )

        return
      }

      let successfulUploads = 0

      for (
        const file
        of selectedFiles
      ) {
        try {
          const result =
            await uploadMutation.mutateAsync(
              {
                file,
                title:
                  file.name.replace(
                    /\.[^.]+$/,
                    "",
                  ),
                department:
                  uploadDepartment,
                document_type:
                  getDocumentType(
                    file.name,
                  ),
              },
            )

          await indexMutation.mutateAsync(
            result.document.id,
          )

          successfulUploads += 1
        } catch (error) {
          toast.error(
            error instanceof Error
              ? `${file.name}: ${error.message}`
              : `${file.name}: upload failed`,
          )
        }
      }

      if (
        successfulUploads > 0
      ) {
        toast.success(
          `${successfulUploads} document(s) uploaded`,
        )
      }

      setSelectedFiles([])
    }

  const handleDelete =
    async (
      document:
        KnowledgeDocument,
    ): Promise<void> => {
      const confirmed =
        window.confirm(
          `Delete "${document.title}"?`,
        )

      if (!confirmed) {
        return
      }

      try {
        await deleteMutation.mutateAsync(
          document.id,
        )

        if (
          selectedDocument?.id ===
          document.id
        ) {
          setSelectedDocument(null)
        }

        toast.success(
          "Document deleted",
        )
      } catch (error) {
        toast.error(
          error instanceof Error
            ? error.message
            : "Delete failed",
        )
      }
    }

  const handleIndex =
    async (
      documentId: string,
    ): Promise<void> => {
      try {
        await indexMutation.mutateAsync(
          documentId,
        )

        toast.success(
          "Document indexing started",
        )
      } catch (error) {
        toast.error(
          error instanceof Error
            ? error.message
            : "Indexing failed",
        )
      }
    }

  return (
    <div className="space-y-6">
      <section className="rounded-2xl bg-gradient-to-r from-violet-600 to-indigo-600 p-6 text-white shadow-lg">
        <p className="text-sm font-medium text-violet-100">
          Enterprise Knowledge Center
        </p>

        <h2 className="mt-2 text-2xl font-bold md:text-3xl">
          Knowledge Base
        </h2>

        <p className="mt-2 max-w-2xl text-sm text-violet-100 md:text-base">
          Upload company documents,
          generate embeddings and ask
          AI questions with verified
          source citations.
        </p>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatisticCard
          title="Total Documents"
          value={String(
            statistics.total,
          )}
          description="Uploaded documents"
          icon={FileText}
        />

        <StatisticCard
          title="Processing Queue"
          value={String(
            statistics.processing,
          )}
          description="Pending documents"
          icon={LoaderCircle}
        />

        <StatisticCard
          title="Indexed Documents"
          value={String(
            statistics.indexed,
          )}
          description="Ready for RAG search"
          icon={Database}
        />

        <StatisticCard
          title="Storage Used"
          value={formatBytes(
            statistics.storage,
          )}
          description="Uploaded file storage"
          icon={File}
        />
      </section>

      <Card>
        <CardHeader>
          <CardTitle>
            Upload Documents
          </CardTitle>

          <CardDescription>
            Upload PDF, DOCX, TXT or
            Markdown files.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          <div
            role="button"
            tabIndex={0}
            onClick={() => {
              fileInputRef.current?.click()
            }}
            onKeyDown={(event) => {
              if (
                event.key === "Enter" ||
                event.key === " "
              ) {
                fileInputRef.current?.click()
              }
            }}
            onDragEnter={(event) => {
              event.preventDefault()
              setIsDragging(true)
            }}
            onDragOver={(event) => {
              event.preventDefault()
              setIsDragging(true)
            }}
            onDragLeave={() => {
              setIsDragging(false)
            }}
            onDrop={handleDrop}
            className={[
              "flex min-h-44 cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-6 text-center transition",
              isDragging
                ? "border-violet-500 bg-violet-50 dark:bg-violet-950/30"
                : "border-border hover:border-violet-400 hover:bg-muted/40",
            ].join(" ")}
          >
            <Upload className="h-10 w-10 text-violet-600" />

            <p className="mt-3 font-medium">
              Drag and drop files here
            </p>

            <p className="mt-1 text-sm text-muted-foreground">
              Or click to select files
            </p>

            <p className="mt-2 text-xs text-muted-foreground">
              Maximum size: 20 MB per
              document
            </p>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.docx,.txt,.md,.markdown"
            className="hidden"
            onChange={
              handleFileChange
            }
          />

          <div className="flex flex-col gap-3 sm:flex-row">
            <select
              value={
                uploadDepartment
              }
              onChange={(event) => {
                setUploadDepartment(
                  event.target.value,
                )
              }}
              className="h-10 rounded-md border bg-background px-3 text-sm"
            >
              {departments
                .filter(
                  (item) =>
                    item !== "All",
                )
                .map((item) => (
                  <option
                    key={item}
                    value={item}
                  >
                    {item}
                  </option>
                ))}
            </select>

            <Button
              type="button"
              disabled={
                selectedFiles.length ===
                  0 ||
                uploadMutation.isPending ||
                indexMutation.isPending
              }
              onClick={() => {
                void handleUpload()
              }}
            >
              {uploadMutation.isPending ||
              indexMutation.isPending ? (
                <LoaderCircle className="h-4 w-4 animate-spin" />
              ) : (
                <Upload className="h-4 w-4" />
              )}

              Upload and Index
            </Button>
          </div>

          {selectedFiles.length >
            0 && (
            <div className="space-y-2 rounded-xl border p-3">
              {selectedFiles.map(
                (file) => (
                  <div
                    key={`${file.name}-${file.size}`}
                    className="flex items-center justify-between gap-3 rounded-lg bg-muted/50 px-3 py-2"
                  >
                    <div className="min-w-0">
                      <p className="truncate text-sm font-medium">
                        {file.name}
                      </p>

                      <p className="text-xs text-muted-foreground">
                        {formatBytes(
                          file.size,
                        )}
                      </p>
                    </div>

                    <Button
                      type="button"
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        removeFile(file)
                      }}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  </div>
                ),
              )}
            </div>
          )}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>
            Documents
          </CardTitle>

          <CardDescription>
            Search, preview, index and
            delete knowledge documents.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          <div className="flex flex-col gap-3 lg:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />

              <Input
                value={search}
                onChange={(event) => {
                  setSearch(
                    event.target.value,
                  )
                }}
                placeholder="Search documents..."
                className="pl-9"
              />
            </div>

            <select
              value={department}
              onChange={(event) => {
                setDepartment(
                  event.target.value,
                )
              }}
              className="h-10 rounded-md border bg-background px-3 text-sm"
            >
              {departments.map(
                (item) => (
                  <option
                    key={item}
                    value={item}
                  >
                    {item}
                  </option>
                ),
              )}
            </select>
          </div>

          {documentsQuery.isLoading ? (
            <div className="flex min-h-56 items-center justify-center">
              <LoaderCircle className="h-8 w-8 animate-spin text-violet-600" />
            </div>
          ) : documentsQuery.isError ? (
            <div className="rounded-xl border border-destructive/30 bg-destructive/5 p-5 text-sm text-destructive">
              Unable to load documents.
              Check whether the backend is
              running.
            </div>
          ) : documents.length === 0 ? (
            <div className="flex min-h-56 flex-col items-center justify-center rounded-xl border border-dashed text-center">
              <Database className="h-10 w-10 text-muted-foreground" />

              <h3 className="mt-3 font-semibold">
                No documents found
              </h3>

              <p className="mt-1 text-sm text-muted-foreground">
                Upload your first company
                document.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto rounded-xl border">
              <table className="w-full min-w-[950px] text-sm">
                <thead className="border-b bg-muted/50 text-left">
                  <tr>
                    <th className="px-4 py-3">
                      Document
                    </th>

                    <th className="px-4 py-3">
                      Department
                    </th>

                    <th className="px-4 py-3">
                      Status
                    </th>

                    <th className="px-4 py-3">
                      Progress
                    </th>

                    <th className="px-4 py-3">
                      Chunks
                    </th>

                    <th className="px-4 py-3">
                      Size
                    </th>

                    <th className="px-4 py-3 text-right">
                      Actions
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {documents.map(
                    (document) => (
                      <tr
                        key={
                          document.id
                        }
                        className="border-b last:border-0"
                      >
                        <td className="px-4 py-3">
                          <button
                            type="button"
                            className="max-w-64 text-left"
                            onClick={() => {
                              setSelectedDocument(
                                document,
                              )
                            }}
                          >
                            <p className="truncate font-medium hover:text-violet-600">
                              {
                                document.title
                              }
                            </p>

                            <p className="truncate text-xs text-muted-foreground">
                              {
                                document.original_file_name ??
                                document.file_name
                              }
                            </p>
                          </button>
                        </td>

                        <td className="px-4 py-3">
                          {document.department ??
                            "General"}
                        </td>

                        <td className="px-4 py-3">
                          <span
                            className={[
                              "inline-flex rounded-full px-2.5 py-1 text-xs font-medium capitalize",
                              getStatusStyle(
                                document.status,
                              ),
                            ].join(" ")}
                          >
                            {
                              document.status
                            }
                          </span>
                        </td>

                        <td className="px-4 py-3">
                          <div className="w-32">
                            <div className="mb-1 text-xs">
                              {
                                document.processing_progress
                              }
                              %
                            </div>

                            <div className="h-2 overflow-hidden rounded-full bg-muted">
                              <div
                                className="h-full rounded-full bg-violet-600 transition-all"
                                style={{
                                  width: `${Math.min(
                                    document.processing_progress,
                                    100,
                                  )}%`,
                                }}
                              />
                            </div>
                          </div>
                        </td>

                        <td className="px-4 py-3">
                          {
                            document.chunk_count
                          }
                        </td>

                        <td className="px-4 py-3">
                          {formatBytes(
                            document.file_size,
                          )}
                        </td>

                        <td className="px-4 py-3">
                          <div className="flex justify-end gap-2">
                            {!isIndexed(
                              document.status,
                            ) && (
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                disabled={
                                  indexMutation.isPending
                                }
                                onClick={() => {
                                  void handleIndex(
                                    document.id,
                                  )
                                }}
                              >
                                <Database className="h-4 w-4" />
                                Index
                              </Button>
                            )}

                            <Button
                              type="button"
                              variant="outline"
                              size="sm"
                              onClick={() => {
                                setSelectedDocument(
                                  document,
                                )
                              }}
                            >
                              <FileText className="h-4 w-4" />
                              Preview
                            </Button>

                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              disabled={
                                deleteMutation.isPending
                              }
                              onClick={() => {
                                void handleDelete(
                                  document,
                                )
                              }}
                            >
                              <Trash2 className="h-4 w-4 text-destructive" />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ),
                  )}
                </tbody>
              </table>
            </div>
          )}
        </CardContent>
      </Card>

      {selectedDocument && (
        <DocumentPreview
          document={
            selectedDocument
          }
          onClose={() => {
            setSelectedDocument(null)
          }}
        />
      )}
    </div>
  )
}

interface StatisticCardProps {
  title: string
  value: string
  description: string
  icon: typeof Database
}

function StatisticCard({
  title,
  value,
  description,
  icon: Icon,
}: StatisticCardProps) {
  return (
    <Card>
      <CardContent className="flex items-start justify-between p-5">
        <div>
          <p className="text-sm text-muted-foreground">
            {title}
          </p>

          <p className="mt-2 text-2xl font-bold">
            {value}
          </p>

          <p className="mt-1 text-xs text-muted-foreground">
            {description}
          </p>
        </div>

        <div className="rounded-xl bg-violet-100 p-3 text-violet-600 dark:bg-violet-950 dark:text-violet-300">
          <Icon className="h-5 w-5" />
        </div>
      </CardContent>
    </Card>
  )
}

interface DocumentPreviewProps {
  document: KnowledgeDocument
  onClose: () => void
}

function DocumentPreview({
  document,
  onClose,
}: DocumentPreviewProps) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4">
      <div className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-2xl border bg-background shadow-2xl">
        <div className="flex items-center justify-between border-b p-5">
          <div>
            <h3 className="font-semibold">
              {document.title}
            </h3>

            <p className="text-sm text-muted-foreground">
              Document information
            </p>
          </div>

          <Button
            type="button"
            variant="ghost"
            size="icon"
            onClick={onClose}
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        <div className="space-y-4 p-5">
          <PreviewRow
            label="File name"
            value={
              document.original_file_name ??
              document.file_name
            }
          />

          <PreviewRow
            label="Department"
            value={
              document.department ??
              "General"
            }
          />

          <PreviewRow
            label="Document type"
            value={
              document.document_type
            }
          />

          <PreviewRow
            label="Status"
            value={document.status}
          />

          <PreviewRow
            label="Progress"
            value={`${document.processing_progress}%`}
          />

          <PreviewRow
            label="Chunks"
            value={String(
              document.chunk_count,
            )}
          />

          <PreviewRow
            label="File size"
            value={formatBytes(
              document.file_size,
            )}
          />

          <PreviewRow
            label="Embedding model"
            value={
              document.embedding_model ??
              "Not generated"
            }
          />

          <PreviewRow
            label="Vector collection"
            value={
              document.vector_collection ??
              "Not indexed"
            }
          />

          <PreviewRow
            label="Created at"
            value={new Date(
              document.created_at,
            ).toLocaleString()}
          />

          {isIndexed(
            document.status,
          ) && (
            <div className="flex items-center gap-2 rounded-xl bg-emerald-50 p-4 text-sm text-emerald-700 dark:bg-emerald-950/30 dark:text-emerald-300">
              <CheckCircle2 className="h-5 w-5" />

              This document is ready
              for RAG search and AI
              chat.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

interface PreviewRowProps {
  label: string
  value: string
}

function PreviewRow({
  label,
  value,
}: PreviewRowProps) {
  return (
    <div className="border-b pb-3 last:border-0">
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
        {label}
      </p>

      <p className="mt-1 break-words text-sm font-medium">
        {value}
      </p>
    </div>
  )
}