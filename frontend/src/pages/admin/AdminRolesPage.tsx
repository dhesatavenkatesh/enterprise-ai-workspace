import { useCallback, useEffect, useState } from "react"
import type { FormEvent } from "react"
import axios from "axios"

import { adminRolesApi } from "@/services/adminApi"
import type {
  AdminRoleCreatePayload,
  AdminRoleListItem,
  AdminRoleListResponse,
  AdminRoleUpdatePayload,
} from "@/types/admin"

interface RoleForm {
  name: string
  description: string
}

const EMPTY_FORM: RoleForm = {
  name: "",
  description: "",
}

function getErrorMessage(error: unknown, fallback: string): string {
  if (!axios.isAxiosError(error)) return fallback
  const detail = error.response?.data?.detail
  return typeof detail === "string" ? detail : fallback
}

export default function AdminRolesPage() {
  const [response, setResponse] =
    useState<AdminRoleListResponse | null>(null)

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")
  const [search, setSearch] = useState("")
  const [page, setPage] = useState(1)

  const [showCreate, setShowCreate] = useState(false)
  const [createForm, setCreateForm] = useState(EMPTY_FORM)
  const [createLoading, setCreateLoading] = useState(false)

  const [editing, setEditing] = useState<AdminRoleListItem | null>(null)
  const [editForm, setEditForm] = useState(EMPTY_FORM)
  const [editLoading, setEditLoading] = useState(false)

  const [deleting, setDeleting] = useState<AdminRoleListItem | null>(null)
  const [deleteLoading, setDeleteLoading] = useState(false)

  const loadRoles = useCallback(async () => {
    try {
      setLoading(true)
      setError("")

      const data = await adminRolesApi.getRoles({
        page,
        page_size: 10,
        search: search.trim() || undefined,
      })

      setResponse(data)
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Unable to load roles."))
    } finally {
      setLoading(false)
    }
  }, [page, search])

  useEffect(() => {
    const timer = window.setTimeout(() => void loadRoles(), 300)
    return () => window.clearTimeout(timer)
  }, [loadRoles])

  const createRole = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()

    const payload: AdminRoleCreatePayload = {
      name: createForm.name.trim(),
      description: createForm.description.trim() || null,
      permission_ids: [],
    }

    try {
      setCreateLoading(true)
      await adminRolesApi.createRole(payload)
      setShowCreate(false)
      setCreateForm(EMPTY_FORM)
      setSuccess("Role created successfully.")
      await loadRoles()
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Unable to create role."))
    } finally {
      setCreateLoading(false)
    }
  }

  const updateRole = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!editing) return

    const payload: AdminRoleUpdatePayload = {
      name: editForm.name.trim(),
      description: editForm.description.trim() || null,
    }

    try {
      setEditLoading(true)
      await adminRolesApi.updateRole(editing.id, payload)
      setEditing(null)
      setSuccess("Role updated successfully.")
      await loadRoles()
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Unable to update role."))
    } finally {
      setEditLoading(false)
    }
  }

  const deleteRole = async () => {
    if (!deleting) return

    try {
      setDeleteLoading(true)
      await adminRolesApi.deleteRole(deleting.id)
      setDeleting(null)
      setSuccess("Role deleted successfully.")
      await loadRoles()
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Unable to delete role."))
    } finally {
      setDeleteLoading(false)
    }
  }

  const totalPages = response?.total_pages ?? 1

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Role Management</h1>
          <p>Create and manage application roles.</p>
        </div>

        <button
          type="button"
          className="primary-button"
          onClick={() => setShowCreate(true)}
        >
          Create Role
        </button>
      </div>

      {success && <div className="admin-success">{success}</div>}

      <input
        type="search"
        value={search}
        placeholder="Search roles"
        onChange={(event) => {
          setPage(1)
          setSearch(event.target.value)
        }}
      />

      {loading && <div className="admin-message">Loading roles...</div>}
      {!loading && error && <div className="admin-error">{error}</div>}

      {!loading && !error && response && (
        <>
          <div className="admin-table-wrapper">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Role</th>
                  <th>Description</th>
                  <th>Permissions</th>
                  <th>Users</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {response.items.map((role) => (
                  <tr key={role.id}>
                    <td>{role.id}</td>
                    <td>{role.name}</td>
                    <td>{role.description ?? "—"}</td>
                    <td>{role.permission_count}</td>
                    <td>{role.user_count}</td>
                    <td>
                      <button
                        type="button"
                        onClick={() => {
                          setEditing(role)
                          setEditForm({
                            name: role.name,
                            description: role.description ?? "",
                          })
                        }}
                      >
                        Edit
                      </button>

                      <button
                        type="button"
                        className="danger-button"
                        disabled={role.user_count > 0}
                        onClick={() => setDeleting(role)}
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
        <RoleModal
          title="Create Role"
          form={createForm}
          setForm={setCreateForm}
          loading={createLoading}
          onSubmit={createRole}
          onClose={() => setShowCreate(false)}
        />
      )}

      {editing && (
        <RoleModal
          title="Edit Role"
          form={editForm}
          setForm={setEditForm}
          loading={editLoading}
          onSubmit={updateRole}
          onClose={() => setEditing(null)}
        />
      )}

      {deleting && (
        <div className="admin-modal-backdrop">
          <div className="admin-modal">
            <h2>Delete Role</h2>
            <p>Delete {deleting.name}?</p>

            <button type="button" onClick={() => setDeleting(null)}>
              Cancel
            </button>

            <button
              type="button"
              className="danger-button"
              disabled={deleteLoading}
              onClick={() => void deleteRole()}
            >
              {deleteLoading ? "Deleting..." : "Delete"}
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

function RoleModal({
  title,
  form,
  setForm,
  loading,
  onSubmit,
  onClose,
}: {
  title: string
  form: RoleForm
  setForm: React.Dispatch<React.SetStateAction<RoleForm>>
  loading: boolean
  onSubmit: (event: FormEvent<HTMLFormElement>) => void
  onClose: () => void
}) {
  return (
    <div className="admin-modal-backdrop">
      <div className="admin-modal">
        <h2>{title}</h2>

        <form onSubmit={onSubmit}>
          <input
            value={form.name}
            placeholder="Role name"
            onChange={(event) =>
              setForm((current) => ({
                ...current,
                name: event.target.value,
              }))
            }
            required
          />

          <textarea
            value={form.description}
            placeholder="Description"
            onChange={(event) =>
              setForm((current) => ({
                ...current,
                description: event.target.value,
              }))
            }
          />

          <button type="button" onClick={onClose}>
            Cancel
          </button>

          <button type="submit" disabled={loading}>
            {loading ? "Saving..." : "Save"}
          </button>
        </form>
      </div>
    </div>
  )
}
