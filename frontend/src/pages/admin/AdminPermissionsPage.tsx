import { useCallback, useEffect, useState } from "react"
import type { FormEvent } from "react"
import axios from "axios"

import { adminPermissionsApi } from "@/services/adminApi"
import type {
  AdminPermission,
  AdminPermissionCreatePayload,
  AdminPermissionListResponse,
  AdminPermissionUpdatePayload,
} from "@/types/admin"

interface PermissionForm {
  permission_name: string
  module: string
  description: string
}

const EMPTY_FORM: PermissionForm = {
  permission_name: "",
  module: "",
  description: "",
}

function getErrorMessage(error: unknown, fallback: string): string {
  if (!axios.isAxiosError(error)) return fallback
  const detail = error.response?.data?.detail
  return typeof detail === "string" ? detail : fallback
}

export default function AdminPermissionsPage() {
  const [response, setResponse] =
    useState<AdminPermissionListResponse | null>(null)

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const [search, setSearch] = useState("")
  const [moduleFilter, setModuleFilter] = useState("")
  const [page, setPage] = useState(1)

  const [showCreate, setShowCreate] = useState(false)
  const [createForm, setCreateForm] = useState(EMPTY_FORM)
  const [createLoading, setCreateLoading] = useState(false)
  const [createError, setCreateError] = useState("")

  const [editing, setEditing] = useState<AdminPermission | null>(null)
  const [editForm, setEditForm] = useState(EMPTY_FORM)
  const [editLoading, setEditLoading] = useState(false)
  const [editError, setEditError] = useState("")

  const [deleting, setDeleting] = useState<AdminPermission | null>(null)
  const [deleteLoading, setDeleteLoading] = useState(false)

  const loadPermissions = useCallback(async () => {
    try {
      setLoading(true)
      setError("")

      const data = await adminPermissionsApi.getPermissions({
        page,
        page_size: 10,
        search: search.trim() || undefined,
        module: moduleFilter.trim() || undefined,
      })

      setResponse(data)
    } catch (requestError) {
      setError(
        getErrorMessage(requestError, "Unable to load permissions."),
      )
    } finally {
      setLoading(false)
    }
  }, [page, search, moduleFilter])

  useEffect(() => {
    const timer = window.setTimeout(() => void loadPermissions(), 300)
    return () => window.clearTimeout(timer)
  }, [loadPermissions])

  const createPermission = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault()

    const payload: AdminPermissionCreatePayload = {
      permission_name: createForm.permission_name.trim(),
      module: createForm.module.trim(),
      description: createForm.description.trim() || null,
    }

    try {
      setCreateLoading(true)
      setCreateError("")
      await adminPermissionsApi.createPermission(payload)
      setShowCreate(false)
      setCreateForm(EMPTY_FORM)
      setSuccess("Permission created successfully.")
      await loadPermissions()
    } catch (requestError) {
      setCreateError(
        getErrorMessage(requestError, "Unable to create permission."),
      )
    } finally {
      setCreateLoading(false)
    }
  }

  const updatePermission = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault()
    if (!editing) return

    const payload: AdminPermissionUpdatePayload = {
      permission_name: editForm.permission_name.trim(),
      module: editForm.module.trim(),
      description: editForm.description.trim() || null,
    }

    try {
      setEditLoading(true)
      setEditError("")
      await adminPermissionsApi.updatePermission(editing.id, payload)
      setEditing(null)
      setSuccess("Permission updated successfully.")
      await loadPermissions()
    } catch (requestError) {
      setEditError(
        getErrorMessage(requestError, "Unable to update permission."),
      )
    } finally {
      setEditLoading(false)
    }
  }

  const deletePermission = async () => {
    if (!deleting) return

    try {
      setDeleteLoading(true)
      await adminPermissionsApi.deletePermission(deleting.id)
      setDeleting(null)
      setSuccess("Permission deleted successfully.")
      await loadPermissions()
    } catch (requestError) {
      setError(
        getErrorMessage(requestError, "Unable to delete permission."),
      )
    } finally {
      setDeleteLoading(false)
    }
  }

  const totalPages = response?.total_pages ?? 1

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Permission Management</h1>
          <p>Create and manage application permissions.</p>
        </div>

        <button
          type="button"
          className="primary-button"
          onClick={() => setShowCreate(true)}
        >
          Create Permission
        </button>
      </div>

      {success && <div className="admin-success">{success}</div>}

      <div className="admin-toolbar">
        <input
          type="search"
          value={search}
          placeholder="Search permissions"
          onChange={(event) => {
            setPage(1)
            setSearch(event.target.value)
          }}
        />

        <input
          value={moduleFilter}
          placeholder="Module"
          onChange={(event) => {
            setPage(1)
            setModuleFilter(event.target.value)
          }}
        />
      </div>

      {loading && <div className="admin-message">Loading permissions...</div>}
      {!loading && error && <div className="admin-error">{error}</div>}

      {!loading && !error && response && (
        <>
          <div className="admin-table-wrapper">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Permission</th>
                  <th>Module</th>
                  <th>Description</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {response.items.map((permission) => (
                  <tr key={permission.id}>
                    <td>{permission.id}</td>
                    <td>{permission.permission_name}</td>
                    <td>{permission.module}</td>
                    <td>{permission.description ?? "—"}</td>
                    <td>
                      <button
                        type="button"
                        onClick={() => {
                          setEditing(permission)
                          setEditForm({
                            permission_name: permission.permission_name,
                            module: permission.module,
                            description: permission.description ?? "",
                          })
                        }}
                      >
                        Edit
                      </button>

                      <button
                        type="button"
                        className="danger-button"
                        onClick={() => setDeleting(permission)}
                      >
                        Delete
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="admin-pagination">
            <button
              type="button"
              disabled={page <= 1}
              onClick={() => setPage((current) => Math.max(1, current - 1))}
            >
              Previous
            </button>

            <span>
              Page {response.page ?? page} of {Math.max(totalPages, 1)}
            </span>

            <button
              type="button"
              disabled={page >= totalPages}
              onClick={() => setPage((current) => current + 1)}
            >
              Next
            </button>
          </div>
        </>
      )}

      {showCreate && (
        <PermissionModal
          title="Create Permission"
          form={createForm}
          setForm={setCreateForm}
          loading={createLoading}
          error={createError}
          onSubmit={createPermission}
          onClose={() => setShowCreate(false)}
        />
      )}

      {editing && (
        <PermissionModal
          title="Edit Permission"
          form={editForm}
          setForm={setEditForm}
          loading={editLoading}
          error={editError}
          onSubmit={updatePermission}
          onClose={() => setEditing(null)}
        />
      )}

      {deleting && (
        <div className="admin-modal-backdrop">
          <div className="admin-modal">
            <h2>Delete Permission</h2>
            <p>Delete {deleting.permission_name}?</p>

            <button type="button" onClick={() => setDeleting(null)}>
              Cancel
            </button>

            <button
              type="button"
              className="danger-button"
              disabled={deleteLoading}
              onClick={() => void deletePermission()}
            >
              {deleteLoading ? "Deleting..." : "Delete"}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
function PermissionModal({
  title,
  form,
  setForm,
  loading,
  error,
  onSubmit,
  onClose,
}: {
  title: string
  form: PermissionForm
  setForm: React.Dispatch<
    React.SetStateAction<PermissionForm>
  >
  loading: boolean
  error: string
  onSubmit: (
    event: FormEvent<HTMLFormElement>,
  ) => void
  onClose: () => void
}) {
  return (
    <div className="admin-modal-backdrop">
      <div className="admin-modal">
        <div className="admin-modal-header">
          <div>
            <h2>{title}</h2>
            <p>
              Enter the permission details below.
            </p>
          </div>

          <button
            type="button"
            disabled={loading}
            onClick={onClose}
            aria-label="Close modal"
          >
            ×
          </button>
        </div>

        <form
          className="admin-form"
          onSubmit={onSubmit}
        >
          <label>
            Permission name

            <input
              type="text"
              value={form.permission_name}
              placeholder="Example: USER_CREATE"
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  permission_name:
                    event.target.value,
                }))
              }
              required
            />
          </label>

          <label>
            Module

            <input
              type="text"
              value={form.module}
              placeholder="Example: users"
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  module:
                    event.target.value,
                }))
              }
              required
            />
          </label>

          <label>
            Description

            <textarea
              rows={4}
              value={form.description}
              placeholder="Describe what this permission allows"
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  description:
                    event.target.value,
                }))
              }
            />
          </label>

          {error && (
            <div className="admin-error">
              <span>{error}</span>
            </div>
          )}

          <div className="admin-form-actions">
            <button
              type="button"
              disabled={loading}
              onClick={onClose}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="primary-button"
              disabled={loading}
            >
              {loading ? "Saving..." : "Save"}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
