import { useCallback, useEffect, useMemo, useState } from "react"
import axios from "axios"

import { adminRolesApi } from "@/services/adminApi"
import type { AdminPermission, AdminRoleListItem } from "@/types/admin"

function getErrorMessage(error: unknown, fallback: string): string {
  if (!axios.isAxiosError(error)) return fallback
  const detail = error.response?.data?.detail
  return typeof detail === "string" ? detail : fallback
}

export default function RolePermissionsPage() {
  const [roles, setRoles] = useState<AdminRoleListItem[]>([])
  const [permissions, setPermissions] = useState<AdminPermission[]>([])
  const [roleId, setRoleId] = useState<number | null>(null)
  const [selectedIds, setSelectedIds] = useState<Set<number>>(new Set())

  const [loading, setLoading] = useState(true)
  const [roleLoading, setRoleLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [search, setSearch] = useState("")
  const [error, setError] = useState("")
  const [success, setSuccess] = useState("")

  const loadInitialData = useCallback(async () => {
    try {
      setLoading(true)
      setError("")

      const [rolesResponse, permissionsResponse] = await Promise.all([
        adminRolesApi.getRoles({ page: 1, page_size: 100 }),
        adminRolesApi.getPermissions(),
      ])

      setRoles(rolesResponse.items)
      setPermissions(permissionsResponse.items)

      if (rolesResponse.items.length > 0) {
        setRoleId((current) => current ?? rolesResponse.items[0].id)
      }
    } catch (requestError) {
      setError(
        getErrorMessage(
          requestError,
          "Unable to load roles and permissions.",
        ),
      )
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadInitialData()
  }, [loadInitialData])

  useEffect(() => {
    if (roleId === null) return

    const loadRole = async () => {
      try {
        setRoleLoading(true)
        setError("")

        const role = await adminRolesApi.getRole(roleId)
        setSelectedIds(
          new Set(role.permissions.map((permission) => permission.id)),
        )
      } catch (requestError) {
        setError(
          getErrorMessage(
            requestError,
            "Unable to load assigned permissions.",
          ),
        )
      } finally {
        setRoleLoading(false)
      }
    }

    void loadRole()
  }, [roleId])

  const groupedPermissions = useMemo(() => {
    const normalizedSearch = search.trim().toLowerCase()

    return permissions
      .filter((permission) => {
        if (!normalizedSearch) return true

        return (
          permission.permission_name
            .toLowerCase()
            .includes(normalizedSearch) ||
          permission.module.toLowerCase().includes(normalizedSearch) ||
          permission.description
            ?.toLowerCase()
            .includes(normalizedSearch)
        )
      })
      .reduce<Record<string, AdminPermission[]>>((groups, permission) => {
        const key = permission.module || "Other"
        if (!groups[key]) groups[key] = []
        groups[key].push(permission)
        return groups
      }, {})
  }, [permissions, search])

  const togglePermission = (permissionId: number) => {
    setSelectedIds((current) => {
      const updated = new Set(current)

      if (updated.has(permissionId)) updated.delete(permissionId)
      else updated.add(permissionId)

      return updated
    })
  }

  const savePermissions = async () => {
    if (roleId === null) return

    try {
      setSaving(true)
      setError("")

      await adminRolesApi.updatePermissions(roleId, {
        permission_ids: Array.from(selectedIds),
      })

      setSuccess("Role permissions updated successfully.")
    } catch (requestError) {
      setError(
        getErrorMessage(
          requestError,
          "Unable to update role permissions.",
        ),
      )
    } finally {
      setSaving(false)
    }
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Role Permission Assignment</h1>
          <p>Assign or remove permissions for each role.</p>
        </div>
      </div>

      {success && <div className="admin-success">{success}</div>}
      {error && <div className="admin-error">{error}</div>}

      {loading ? (
        <div className="admin-message">Loading RBAC data...</div>
      ) : (
        <>
          <div className="admin-toolbar">
            <select
              value={roleId ?? ""}
              onChange={(event) => {
                setRoleId(Number(event.target.value))
                setSuccess("")
              }}
            >
              {roles.map((role) => (
                <option key={role.id} value={role.id}>
                  {role.name}
                </option>
              ))}
            </select>

            <input
              type="search"
              value={search}
              placeholder="Search permissions"
              onChange={(event) => setSearch(event.target.value)}
            />

            <button
              type="button"
              onClick={() =>
                setSelectedIds(
                  new Set(permissions.map((permission) => permission.id)),
                )
              }
            >
              Select All
            </button>

            <button type="button" onClick={() => setSelectedIds(new Set())}>
              Clear All
            </button>
          </div>

          {roleLoading ? (
            <div className="admin-message">
              Loading assigned permissions...
            </div>
          ) : (
            <div className="permission-groups">
              {Object.entries(groupedPermissions).map(
                ([moduleName, modulePermissions]) => (
                  <section key={moduleName} className="permission-group">
                    <h2>{moduleName}</h2>

                    <div className="permission-grid">
                      {modulePermissions.map((permission) => (
                        <label
                          key={permission.id}
                          className="permission-checkbox-card"
                        >
                          <input
                            type="checkbox"
                            checked={selectedIds.has(permission.id)}
                            onChange={() => togglePermission(permission.id)}
                          />

                          <span>
                            <strong>{permission.permission_name}</strong>
                            <small>{permission.module}</small>
                            {permission.description && (
                              <small>{permission.description}</small>
                            )}
                          </span>
                        </label>
                      ))}
                    </div>
                  </section>
                ),
              )}
            </div>
          )}

          <div className="admin-form-actions">
            <span>{selectedIds.size} permission(s) selected</span>

            <button
              type="button"
              className="primary-button"
              disabled={saving || roleId === null || roleLoading}
              onClick={() => void savePermissions()}
            >
              {saving ? "Saving..." : "Save Permissions"}
            </button>
          </div>
        </>
      )}
    </div>
  )
}
