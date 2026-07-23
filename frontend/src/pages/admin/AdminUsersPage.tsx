import {
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react"
import type {
  Dispatch,
  FormEvent,
  SetStateAction,
} from "react"
import axios from "axios"

import {
  adminRolesApi,
  adminUsersApi,
} from "@/services/adminApi"

import type {
  AdminPasswordResetPayload,
  AdminRoleListItem,
  AdminUser,
  AdminUserCreatePayload,
  AdminUserListResponse,
  AdminUserUpdatePayload,
} from "@/types/admin"

interface UserFormState {
  name: string
  email: string
  password: string
  role_id: string
  is_active: boolean
}

interface PasswordFormState {
  new_password: string
  confirm_password: string
  force_logout: boolean
}

const EMPTY_USER_FORM: UserFormState = {
  name: "",
  email: "",
  password: "",
  role_id: "",
  is_active: true,
}

const EMPTY_PASSWORD_FORM: PasswordFormState = {
  new_password: "",
  confirm_password: "",
  force_logout: true,
}

const PAGE_SIZE = 10

function getErrorMessage(
  error: unknown,
  fallback: string,
): string {
  if (!axios.isAxiosError(error)) {
    return fallback
  }

  const detail = error.response?.data?.detail

  if (typeof detail === "string") {
    return detail
  }

  if (Array.isArray(detail)) {
    return detail
      .map((item) => {
        if (
          typeof item === "object" &&
          item !== null &&
          "msg" in item
        ) {
          return String(item.msg)
        }

        return String(item)
      })
      .join(", ")
  }

  const message = error.response?.data?.message

  if (typeof message === "string") {
    return message
  }

  return fallback
}

function formatDate(value: string | null): string {
  if (!value) {
    return "—"
  }

  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return date.toLocaleString()
}

export default function AdminUsersPage() {
  const [response, setResponse] =
    useState<AdminUserListResponse | null>(null)

  const [roles, setRoles] =
    useState<AdminRoleListItem[]>([])

  const [page, setPage] = useState(1)
  const [search, setSearch] = useState("")

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  const [showCreateModal, setShowCreateModal] =
    useState(false)

  const [createForm, setCreateForm] =
    useState<UserFormState>(EMPTY_USER_FORM)

  const [createLoading, setCreateLoading] =
    useState(false)

  const [createError, setCreateError] = useState("")

  const [editingUser, setEditingUser] =
    useState<AdminUser | null>(null)

  const [editForm, setEditForm] =
    useState<UserFormState>(EMPTY_USER_FORM)

  const [editLoading, setEditLoading] =
    useState(false)

  const [editError, setEditError] = useState("")

  const [passwordUser, setPasswordUser] =
    useState<AdminUser | null>(null)

  const [passwordForm, setPasswordForm] =
    useState<PasswordFormState>(
      EMPTY_PASSWORD_FORM,
    )

  const [passwordLoading, setPasswordLoading] =
    useState(false)

  const [passwordError, setPasswordError] =
    useState("")

  const [statusUser, setStatusUser] =
    useState<AdminUser | null>(null)

  const [statusLoading, setStatusLoading] =
    useState(false)

  const [statusError, setStatusError] =
    useState("")

  const [deletingUser, setDeletingUser] =
    useState<AdminUser | null>(null)

  const [deleteLoading, setDeleteLoading] =
    useState(false)

  const [deleteError, setDeleteError] =
    useState("")

  const loadUsers = useCallback(async () => {
    try {
      setLoading(true)
      setError("")

      const data = await adminUsersApi.getUsers({
        page,
        page_size: PAGE_SIZE,
        search: search.trim() || undefined,
        include_deleted: false,
      })

      setResponse(data)
    } catch (requestError) {
      setError(
        getErrorMessage(
          requestError,
          "Unable to load users.",
        ),
      )
    } finally {
      setLoading(false)
    }
  }, [page, search])

  const loadRoles = useCallback(async () => {
    try {
      const data = await adminRolesApi.getRoles({
        page: 1,
        page_size: 100,
      })

      setRoles(data.items)
    } catch (requestError) {
      setError(
        getErrorMessage(
          requestError,
          "Unable to load roles.",
        ),
      )
    }
  }, [])

  useEffect(() => {
    const timer = window.setTimeout(() => {
      void loadUsers()
    }, 300)

    return () => {
      window.clearTimeout(timer)
    }
  }, [loadUsers])

  useEffect(() => {
    void loadRoles()
  }, [loadRoles])

  useEffect(() => {
    if (!success) {
      return
    }

    const timer = window.setTimeout(() => {
      setSuccess("")
    }, 3000)

    return () => {
      window.clearTimeout(timer)
    }
  }, [success])

  const totalPages = useMemo(() => {
    return Math.max(response?.total_pages ?? 1, 1)
  }, [response])

  const validateUserForm = (
    form: UserFormState,
    requirePassword: boolean,
  ): string => {
    if (!form.name.trim()) {
      return "Name is required."
    }

    if (!form.email.trim()) {
      return "Email is required."
    }

    if (!form.email.includes("@")) {
      return "Enter a valid email address."
    }

    if (requirePassword && form.password.length < 8) {
      return "Password must contain at least 8 characters."
    }

    return ""
  }

  const openCreateModal = () => {
    setCreateForm(EMPTY_USER_FORM)
    setCreateError("")
    setShowCreateModal(true)
  }

  const handleCreateUser = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault()

    const validationError = validateUserForm(
      createForm,
      true,
    )

    if (validationError) {
      setCreateError(validationError)
      return
    }

    const payload: AdminUserCreatePayload = {
      name: createForm.name.trim(),
      email: createForm.email.trim(),
      password: createForm.password,
      role_id: createForm.role_id
        ? Number(createForm.role_id)
        : null,
      is_active: createForm.is_active,
    }

    try {
      setCreateLoading(true)
      setCreateError("")

      await adminUsersApi.createUser(payload)

      setShowCreateModal(false)
      setCreateForm(EMPTY_USER_FORM)
      setSuccess("User created successfully.")
      setPage(1)

      await loadUsers()
    } catch (requestError) {
      setCreateError(
        getErrorMessage(
          requestError,
          "Unable to create user.",
        ),
      )
    } finally {
      setCreateLoading(false)
    }
  }

  const openEditModal = (user: AdminUser) => {
    setEditingUser(user)

    setEditForm({
      name: user.name,
      email: user.email,
      password: "",
      role_id:
        user.role_id === null
          ? ""
          : String(user.role_id),
      is_active: user.is_active,
    })

    setEditError("")
  }

  const handleUpdateUser = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault()

    if (!editingUser) {
      return
    }

    const validationError = validateUserForm(
      editForm,
      false,
    )

    if (validationError) {
      setEditError(validationError)
      return
    }

    const payload: AdminUserUpdatePayload = {
      name: editForm.name.trim(),
      email: editForm.email.trim(),
      role_id: editForm.role_id
        ? Number(editForm.role_id)
        : null,
      is_active: editForm.is_active,
    }

    try {
      setEditLoading(true)
      setEditError("")

      await adminUsersApi.updateUser(
        editingUser.id,
        payload,
      )

      setEditingUser(null)
      setSuccess("User updated successfully.")

      await loadUsers()
    } catch (requestError) {
      setEditError(
        getErrorMessage(
          requestError,
          "Unable to update user.",
        ),
      )
    } finally {
      setEditLoading(false)
    }
  }

  const openPasswordModal = (user: AdminUser) => {
    setPasswordUser(user)
    setPasswordForm(EMPTY_PASSWORD_FORM)
    setPasswordError("")
  }

  const handleResetPassword = async (
    event: FormEvent<HTMLFormElement>,
  ) => {
    event.preventDefault()

    if (!passwordUser) {
      return
    }

    if (passwordForm.new_password.length < 8) {
      setPasswordError(
        "Password must contain at least 8 characters.",
      )
      return
    }

    if (
      passwordForm.new_password !==
      passwordForm.confirm_password
    ) {
      setPasswordError("Passwords do not match.")
      return
    }

    const payload: AdminPasswordResetPayload = {
      new_password: passwordForm.new_password,
      confirm_password:
        passwordForm.confirm_password,
      force_logout: passwordForm.force_logout,
    }

    try {
      setPasswordLoading(true)
      setPasswordError("")

      await adminUsersApi.resetPassword(
        passwordUser.id,
        payload,
      )

      setPasswordUser(null)
      setPasswordForm(EMPTY_PASSWORD_FORM)

      setSuccess(
        `Password reset successfully for ${passwordUser.name}.`,
      )
    } catch (requestError) {
      setPasswordError(
        getErrorMessage(
          requestError,
          "Unable to reset password.",
        ),
      )
    } finally {
      setPasswordLoading(false)
    }
  }

  const openStatusModal = (user: AdminUser) => {
    setStatusUser(user)
    setStatusError("")
  }

  const handleToggleStatus = async () => {
    if (!statusUser) {
      return
    }

    const newStatus = !statusUser.is_active

    try {
      setStatusLoading(true)
      setStatusError("")

      await adminUsersApi.updateUserStatus(
        statusUser.id,
        {
          is_active: newStatus,
        },
      )

      setStatusUser(null)

      setSuccess(
        newStatus
          ? "User activated successfully."
          : "User deactivated successfully.",
      )

      await loadUsers()
    } catch (requestError) {
      setStatusError(
        getErrorMessage(
          requestError,
          "Unable to update user status.",
        ),
      )
    } finally {
      setStatusLoading(false)
    }
  }

  const openDeleteModal = (user: AdminUser) => {
    setDeletingUser(user)
    setDeleteError("")
  }

  const handleDeleteUser = async () => {
    if (!deletingUser) {
      return
    }

    try {
      setDeleteLoading(true)
      setDeleteError("")

      await adminUsersApi.deleteUser(
        deletingUser.id,
      )

      setDeletingUser(null)
      setSuccess("User deleted successfully.")

      if (
        response?.items.length === 1 &&
        page > 1
      ) {
        setPage((current) => current - 1)
      } else {
        await loadUsers()
      }
    } catch (requestError) {
      setDeleteError(
        getErrorMessage(
          requestError,
          "Unable to delete user.",
        ),
      )
    } finally {
      setDeleteLoading(false)
    }
  }

  return (
    <div className="admin-users-page">
      <div className="admin-users-header">
        <div>
          <h1>User Management</h1>

          <p>
            Create users, assign roles and manage
            account access.
          </p>
        </div>

        <button
          type="button"
          className="create-user-button"
          onClick={openCreateModal}
        >
          <span aria-hidden="true">＋</span>
          Create User
        </button>
      </div>

      {success && (
        <div className="admin-success-message">
          {success}
        </div>
      )}

      <div className="admin-users-search">
        <span
          className="search-icon"
          aria-hidden="true"
        >
          ⌕
        </span>

        <input
          type="search"
          value={search}
          placeholder="Search by name or email"
          aria-label="Search users"
          onChange={(event) => {
            setPage(1)
            setSearch(event.target.value)
          }}
        />
      </div>

      {loading && (
        <div className="admin-loading-message">
          Loading users...
        </div>
      )}

      {!loading && error && (
        <div className="admin-error-message">
          <span>{error}</span>

          <button
            type="button"
            onClick={() => void loadUsers()}
          >
            Retry
          </button>
        </div>
      )}

      {!loading && !error && response && (
        <>
          <div className="admin-users-table-wrapper">
            <table className="admin-users-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>User</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th>Created</th>
                  <th>Updated</th>
                  <th>Actions</th>
                </tr>
              </thead>

              <tbody>
                {response.items.length === 0 ? (
                  <tr>
                    <td
                      colSpan={7}
                      className="empty-users-cell"
                    >
                      No users found.
                    </td>
                  </tr>
                ) : (
                  response.items.map((user) => (
                    <tr key={user.id}>
                      <td>{user.id}</td>

                      <td>
                        <div className="user-information">
                          <strong>{user.name}</strong>
                          <span>{user.email}</span>
                        </div>
                      </td>

                      <td>
                        {user.role_name ?? "No role"}
                      </td>

                      <td>
                        <span
                          className={
                            user.is_active
                              ? "user-status-badge active"
                              : "user-status-badge inactive"
                          }
                        >
                          {user.is_active
                            ? "Active"
                            : "Inactive"}
                        </span>
                      </td>

                      <td>
                        {formatDate(user.created_at)}
                      </td>

                      <td>
                        {formatDate(user.updated_at)}
                      </td>

                      <td className="actions-table-cell">
                        <div className="user-action-buttons">
                          <button
                            type="button"
                            className="
                              user-action-button
                              edit-action-button
                            "
                            onClick={() =>
                              openEditModal(user)
                            }
                          >
                            <span
                              className="action-icon"
                              aria-hidden="true"
                            >
                              ✎
                            </span>

                            Edit
                          </button>

                          <button
                            type="button"
                            className="
                              user-action-button
                              reset-action-button
                            "
                            onClick={() =>
                              openPasswordModal(user)
                            }
                          >
                            <span
                              className="action-icon"
                              aria-hidden="true"
                            >
                              ▣
                            </span>

                            Reset Password
                          </button>

                          <button
                            type="button"
                            className={
                              user.is_active
                                ? `
                                  user-action-button
                                  deactivate-action-button
                                `
                                : `
                                  user-action-button
                                  activate-action-button
                                `
                            }
                            onClick={() =>
                              openStatusModal(user)
                            }
                          >
                            <span
                              className="action-icon"
                              aria-hidden="true"
                            >
                              ⊙
                            </span>

                            {user.is_active
                              ? "Deactivate"
                              : "Activate"}
                          </button>

                          <button
                            type="button"
                            className="
                              user-action-button
                              delete-action-button
                            "
                            onClick={() =>
                              openDeleteModal(user)
                            }
                          >
                            <span
                              className="action-icon"
                              aria-hidden="true"
                            >
                              ♲
                            </span>

                            Delete
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          <div className="users-table-footer">
            <p>
              Total users:{" "}
              <strong>{response.total}</strong>
            </p>

            <div className="users-pagination">
              <button
                type="button"
                disabled={page <= 1}
                onClick={() =>
                  setPage((current) =>
                    Math.max(1, current - 1),
                  )
                }
              >
                Previous
              </button>

              <span>
                Page {response.page} of{" "}
                {totalPages}
              </span>

              <button
                type="button"
                disabled={page >= totalPages}
                onClick={() =>
                  setPage((current) => current + 1)
                }
              >
                Next
              </button>
            </div>
          </div>
        </>
      )}

      {showCreateModal && (
        <UserFormModal
          title="Create User"
          form={createForm}
          setForm={setCreateForm}
          roles={roles}
          loading={createLoading}
          error={createError}
          requirePassword
          submitText="Create User"
          onSubmit={handleCreateUser}
          onClose={() =>
            setShowCreateModal(false)
          }
        />
      )}

      {editingUser && (
        <UserFormModal
          title="Edit User"
          form={editForm}
          setForm={setEditForm}
          roles={roles}
          loading={editLoading}
          error={editError}
          requirePassword={false}
          submitText="Save Changes"
          onSubmit={handleUpdateUser}
          onClose={() => setEditingUser(null)}
        />
      )}

      {passwordUser && (
        <div className="admin-modal-backdrop">
          <div className="admin-user-modal">
            <div className="admin-modal-header">
              <div>
                <h2>Reset Password</h2>

                <p>
                  Reset password for{" "}
                  <strong>
                    {passwordUser.name}
                  </strong>
                </p>
              </div>

              <button
                type="button"
                className="modal-close-button"
                disabled={passwordLoading}
                onClick={() =>
                  setPasswordUser(null)
                }
              >
                ×
              </button>
            </div>

            <form
              className="admin-user-form"
              onSubmit={handleResetPassword}
            >
              <label>
                New password

                <input
                  type="password"
                  value={
                    passwordForm.new_password
                  }
                  minLength={8}
                  onChange={(event) =>
                    setPasswordForm(
                      (current) => ({
                        ...current,
                        new_password:
                          event.target.value,
                      }),
                    )
                  }
                  required
                />
              </label>

              <label>
                Confirm password

                <input
                  type="password"
                  value={
                    passwordForm.confirm_password
                  }
                  minLength={8}
                  onChange={(event) =>
                    setPasswordForm(
                      (current) => ({
                        ...current,
                        confirm_password:
                          event.target.value,
                      }),
                    )
                  }
                  required
                />
              </label>

              <label className="checkbox-field">
                <input
                  type="checkbox"
                  checked={
                    passwordForm.force_logout
                  }
                  onChange={(event) =>
                    setPasswordForm(
                      (current) => ({
                        ...current,
                        force_logout:
                          event.target.checked,
                      }),
                    )
                  }
                />

                Force logout from existing sessions
              </label>

              {passwordError && (
                <div className="modal-error-message">
                  {passwordError}
                </div>
              )}

              <div className="admin-modal-actions">
                <button
                  type="button"
                  className="modal-cancel-button"
                  disabled={passwordLoading}
                  onClick={() =>
                    setPasswordUser(null)
                  }
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className="modal-submit-button"
                  disabled={passwordLoading}
                >
                  {passwordLoading
                    ? "Resetting..."
                    : "Reset Password"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {statusUser && (
        <ConfirmationModal
          title={
            statusUser.is_active
              ? "Deactivate User"
              : "Activate User"
          }
          message={
            statusUser.is_active
              ? `Deactivate ${statusUser.name}? The user will no longer be able to access the application.`
              : `Activate ${statusUser.name}? The user will regain access to the application.`
          }
          confirmText={
            statusUser.is_active
              ? "Deactivate"
              : "Activate"
          }
          confirmClassName={
            statusUser.is_active
              ? "warning-confirm-button"
              : "success-confirm-button"
          }
          loading={statusLoading}
          error={statusError}
          onConfirm={() =>
            void handleToggleStatus()
          }
          onClose={() => setStatusUser(null)}
        />
      )}

      {deletingUser && (
        <ConfirmationModal
          title="Delete User"
          message={`Delete ${deletingUser.name}? This action cannot be undone.`}
          confirmText="Delete"
          confirmClassName="danger-confirm-button"
          loading={deleteLoading}
          error={deleteError}
          onConfirm={() =>
            void handleDeleteUser()
          }
          onClose={() =>
            setDeletingUser(null)
          }
        />
      )}
    </div>
  )
}

function UserFormModal({
  title,
  form,
  setForm,
  roles,
  loading,
  error,
  requirePassword,
  submitText,
  onSubmit,
  onClose,
}: {
  title: string
  form: UserFormState
  setForm: Dispatch<
    SetStateAction<UserFormState>
  >
  roles: AdminRoleListItem[]
  loading: boolean
  error: string
  requirePassword: boolean
  submitText: string
  onSubmit: (
    event: FormEvent<HTMLFormElement>,
  ) => void
  onClose: () => void
}) {
  return (
    <div className="admin-modal-backdrop">
      <div className="admin-user-modal">
        <div className="admin-modal-header">
          <h2>{title}</h2>

          <button
            type="button"
            className="modal-close-button"
            disabled={loading}
            onClick={onClose}
          >
            ×
          </button>
        </div>

        <form
          className="admin-user-form"
          onSubmit={onSubmit}
        >
          <label>
            Name

            <input
              type="text"
              value={form.name}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  name: event.target.value,
                }))
              }
              required
            />
          </label>

          <label>
            Email address

            <input
              type="email"
              value={form.email}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  email: event.target.value,
                }))
              }
              required
            />
          </label>

          {requirePassword && (
            <label>
              Password

              <input
                type="password"
                value={form.password}
                minLength={8}
                onChange={(event) =>
                  setForm((current) => ({
                    ...current,
                    password:
                      event.target.value,
                  }))
                }
                required
              />
            </label>
          )}

          <label>
            Role

            <select
              value={form.role_id}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  role_id:
                    event.target.value,
                }))
              }
            >
              <option value="">
                No role
              </option>

              {roles.map((role) => (
                <option
                  key={role.id}
                  value={role.id}
                >
                  {role.name}
                </option>
              ))}
            </select>
          </label>

          <label className="checkbox-field">
            <input
              type="checkbox"
              checked={form.is_active}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  is_active:
                    event.target.checked,
                }))
              }
            />

            Active account
          </label>

          {error && (
            <div className="modal-error-message">
              {error}
            </div>
          )}

          <div className="admin-modal-actions">
            <button
              type="button"
              className="modal-cancel-button"
              disabled={loading}
              onClick={onClose}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="modal-submit-button"
              disabled={loading}
            >
              {loading
                ? "Saving..."
                : submitText}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function ConfirmationModal({
  title,
  message,
  confirmText,
  confirmClassName,
  loading,
  error,
  onConfirm,
  onClose,
}: {
  title: string
  message: string
  confirmText: string
  confirmClassName: string
  loading: boolean
  error: string
  onConfirm: () => void
  onClose: () => void
}) {
  return (
    <div className="admin-modal-backdrop">
      <div className="admin-user-modal confirmation-modal">
        <div className="admin-modal-header">
          <h2>{title}</h2>

          <button
            type="button"
            className="modal-close-button"
            disabled={loading}
            onClick={onClose}
          >
            ×
          </button>
        </div>

        <p className="confirmation-message">
          {message}
        </p>

        {error && (
          <div className="modal-error-message">
            {error}
          </div>
        )}

        <div className="admin-modal-actions">
          <button
            type="button"
            className="modal-cancel-button"
            disabled={loading}
            onClick={onClose}
          >
            Cancel
          </button>

          <button
            type="button"
            className={confirmClassName}
            disabled={loading}
            onClick={onConfirm}
          >
            {loading
              ? "Processing..."
              : confirmText}
          </button>
        </div>
      </div>
    </div>
  )
}