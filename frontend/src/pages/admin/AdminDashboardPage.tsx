import {
  Activity,
  RefreshCw,
  ShieldCheck,
  UserCheck,
  UserMinus,
  UserRoundX,
  Users,
} from "lucide-react"

import {
  useCallback,
  useEffect,
  useState,
} from "react"

import axios from "axios"

import {
  adminDashboardApi,
} from "@/services/adminApi"

import type {
  AdminDashboardResponse,
} from "@/types/admin"

import "@/styles/AdminDashboardPage.css"

function getErrorMessage(
  error: unknown,
  fallback: string,
): string {
  if (!axios.isAxiosError(error)) {
    return fallback
  }

  const detail =
    error.response?.data?.detail

  if (typeof detail === "string") {
    return detail
  }

  const message =
    error.response?.data?.message

  if (typeof message === "string") {
    return message
  }

  return fallback
}

function formatDate(
  value: string,
): string {
  const date = new Date(value)

  if (Number.isNaN(date.getTime())) {
    return value
  }

  return date.toLocaleString()
}

export default function AdminDashboardPage() {
  const [
    dashboard,
    setDashboard,
  ] = useState<AdminDashboardResponse | null>(
    null,
  )

  const [
    loading,
    setLoading,
  ] = useState(true)

  const [
    refreshing,
    setRefreshing,
  ] = useState(false)

  const [
    error,
    setError,
  ] = useState("")

  const loadDashboard =
    useCallback(
      async (
        showRefreshState = false,
      ) => {
        try {
          if (showRefreshState) {
            setRefreshing(true)
          } else {
            setLoading(true)
          }

          setError("")

          const data =
            await adminDashboardApi.getDashboard()

          setDashboard(data)
        } catch (requestError) {
          setError(
            getErrorMessage(
              requestError,
              "Unable to load admin dashboard.",
            ),
          )
        } finally {
          setLoading(false)
          setRefreshing(false)
        }
      },
      [],
    )

  useEffect(() => {
    void loadDashboard()
  }, [loadDashboard])

  if (loading) {
    return (
      <div className="admin-dashboard-page">
        <div className="admin-dashboard-loading">
          Loading admin dashboard...
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="admin-dashboard-page">
        <div className="admin-dashboard-error">
          <span>{error}</span>

          <button
            type="button"
            onClick={() =>
              void loadDashboard()
            }
          >
            Retry
          </button>
        </div>
      </div>
    )
  }

  if (!dashboard) {
    return null
  }

  const statistics = [
    {
      title: "Total Users",
      value: dashboard.users.total,
      description:
        "All registered user accounts",
      icon: Users,
      variant: "blue",
    },
    {
      title: "Active Users",
      value: dashboard.users.active,
      description:
        "Accounts currently enabled",
      icon: UserCheck,
      variant: "green",
    },
    {
      title: "Inactive Users",
      value: dashboard.users.inactive,
      description:
        "Accounts currently disabled",
      icon: UserMinus,
      variant: "amber",
    },
    {
      title: "Locked Users",
      value: dashboard.users.locked,
      description:
        "Accounts restricted from login",
      icon: UserRoundX,
      variant: "red",
    },
    {
      title: "Deleted Users",
      value: dashboard.users.deleted,
      description:
        "Soft-deleted user accounts",
      icon: UserRoundX,
      variant: "slate",
    },
    {
      title: "Roles",
      value: dashboard.roles.total_roles,
      description:
        "Available RBAC roles",
      icon: ShieldCheck,
      variant: "violet",
    },
    {
      title: "Permissions",
      value:
        dashboard.roles.total_permissions,
      description:
        "Configured RBAC permissions",
      icon: ShieldCheck,
      variant: "indigo",
    },
    {
      title: "Audit Logs Today",
      value:
        dashboard.audit.logs_today,
      description: `${dashboard.audit.total_logs} total audit records`,
      icon: Activity,
      variant: "cyan",
    },
  ] as const

  return (
    <div className="admin-dashboard-page">
      <div className="admin-dashboard-header">
        <div>
          <h1>Admin Dashboard</h1>

          <p>
            Monitor users, roles,
            permissions and administrative
            activity.
          </p>
        </div>

        <button
          type="button"
          className="admin-refresh-button"
          disabled={refreshing}
          onClick={() =>
            void loadDashboard(true)
          }
        >
          <RefreshCw
            className={
              refreshing
                ? "admin-refresh-icon spinning"
                : "admin-refresh-icon"
            }
          />

          {refreshing
            ? "Refreshing..."
            : "Refresh"}
        </button>
      </div>

      <div className="admin-stat-grid">
        {statistics.map((item) => {
          const Icon = item.icon

          return (
            <article
              key={item.title}
              className={`admin-stat-card admin-stat-${item.variant}`}
            >
              <div className="admin-stat-card-top">
                <div>
                  <p className="admin-stat-title">
                    {item.title}
                  </p>

                  <p className="admin-stat-value">
                    {item.value}
                  </p>
                </div>

                <div className="admin-stat-icon">
                  <Icon />
                </div>
              </div>

              <p className="admin-stat-description">
                {item.description}
              </p>
            </article>
          )
        })}
      </div>

      <section className="admin-dashboard-section">
        <div className="admin-section-heading">
          <div className="admin-section-icon">
            <Activity />
          </div>

          <div>
            <h2>Recent Audit Activity</h2>

            <p>
              Latest administrative and
              security events.
            </p>
          </div>
        </div>

        <div className="admin-recent-table-wrapper">
          <table className="admin-recent-table">
            <thead>
              <tr>
                <th>ID</th>
                <th>User</th>
                <th>Action</th>
                <th>Resource</th>
                <th>IP Address</th>
                <th>Date</th>
              </tr>
            </thead>

            <tbody>
              {dashboard.recent_audit_logs
                .length === 0 ? (
                <tr>
                  <td
                    colSpan={6}
                    className="admin-empty-cell"
                  >
                    No recent audit activity.
                  </td>
                </tr>
              ) : (
                dashboard.recent_audit_logs.map(
                  (log) => (
                    <tr key={log.id}>
                      <td>{log.id}</td>

                      <td>
                        {log.user_id === null
                          ? "System"
                          : `User ${log.user_id}`}
                      </td>

                      <td>
                        <span className="admin-action-code">
                          {log.action}
                        </span>
                      </td>

                      <td>
                        {log.resource}

                        {log.resource_id !==
                          null && (
                          <span className="admin-resource-id">
                            #{log.resource_id}
                          </span>
                        )}
                      </td>

                      <td>
                        {log.ip_address ??
                          "—"}
                      </td>

                      <td>
                        {formatDate(
                          log.created_at,
                        )}
                      </td>
                    </tr>
                  ),
                )
              )}
            </tbody>
          </table>
        </div>
      </section>

      <p className="admin-generated-time">
        Dashboard generated at{" "}
        {formatDate(
          dashboard.generated_at,
        )}
      </p>
    </div>
  )
}