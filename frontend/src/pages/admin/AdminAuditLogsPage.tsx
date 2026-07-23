import { useCallback, useEffect, useState } from "react"
import axios from "axios"

import { adminAuditApi } from "@/services/adminApi"
import type { AdminAuditLog, AdminAuditLogListResponse } from "@/types/admin"

const PAGE_SIZE = 20

function getErrorMessage(error: unknown, fallback: string): string {
  if (!axios.isAxiosError(error)) return fallback
  const detail = error.response?.data?.detail
  return typeof detail === "string" ? detail : fallback
}

function formatDate(value: string): string {
  const date = new Date(value)
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString()
}

function formatDetails(details: AdminAuditLog["details"]): string {
  if (details === null || details === undefined) return "No details"
  if (typeof details === "string") return details

  try {
    return JSON.stringify(details, null, 2)
  } catch {
    return "Unable to display details"
  }
}

export default function AdminAuditLogsPage() {
  const [response, setResponse] =
    useState<AdminAuditLogListResponse | null>(null)

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState("")
  const [action, setAction] = useState("")
  const [resource, setResource] = useState("")
  const [ipAddress, setIpAddress] = useState("")
  const [dateFrom, setDateFrom] = useState("")
  const [dateTo, setDateTo] = useState("")
  const [page, setPage] = useState(1)

  const loadLogs = useCallback(async () => {
    if (dateFrom && dateTo && dateFrom > dateTo) {
      setLoading(false)
      setError("The From date cannot be later than the To date.")
      return
    }

    try {
      setLoading(true)
      setError("")

      const data = await adminAuditApi.getAuditLogs({
        page,
        page_size: PAGE_SIZE,
        action: action.trim() || undefined,
        resource: resource.trim() || undefined,
        ip_address: ipAddress.trim() || undefined,
        start_date: dateFrom || undefined,
        end_date: dateTo || undefined,
      })

      setResponse(data)
    } catch (requestError) {
      setError(getErrorMessage(requestError, "Unable to load audit logs."))
    } finally {
      setLoading(false)
    }
  }, [page, action, resource, ipAddress, dateFrom, dateTo])

  useEffect(() => {
    const timer = window.setTimeout(() => void loadLogs(), 300)
    return () => window.clearTimeout(timer)
  }, [loadLogs])

  const clearFilters = () => {
    setAction("")
    setResource("")
    setIpAddress("")
    setDateFrom("")
    setDateTo("")
    setPage(1)
    setError("")
  }

  const exportCsv = () => {
    if (!response?.items.length) return

    const headers = [
      "ID",
      "User ID",
      "Action",
      "Resource",
      "Resource ID",
      "IP Address",
      "Created At",
    ]

    const rows = response.items.map((log) => [
      log.id,
      log.user_id ?? "",
      log.action,
      log.resource,
      log.resource_id ?? "",
      log.ip_address ?? "",
      log.created_at,
    ])

    const csv = [headers, ...rows]
      .map((row) =>
        row
          .map((value) => `"${String(value).replace(/"/g, '""')}"`)
          .join(","),
      )
      .join("\n")

    const blob = new Blob([`\uFEFF${csv}`], {
      type: "text/csv;charset=utf-8",
    })

    const url = URL.createObjectURL(blob)
    const anchor = document.createElement("a")
    anchor.href = url
    anchor.download = `audit-logs-page-${page}.csv`
    anchor.click()
    URL.revokeObjectURL(url)
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <div>
          <h1>Audit Logs</h1>
          <p>Track user and security-sensitive activity.</p>
        </div>

        <button
          type="button"
          className="secondary-button"
          disabled={loading || !response?.items.length}
          onClick={exportCsv}
        >
          Export Current Page
        </button>
      </div>

      <div className="admin-toolbar audit-filter-toolbar">
        <input
          value={action}
          placeholder="Action"
          onChange={(event) => {
            setPage(1)
            setAction(event.target.value)
          }}
        />

        <input
          value={resource}
          placeholder="Resource"
          onChange={(event) => {
            setPage(1)
            setResource(event.target.value)
          }}
        />

        <input
          value={ipAddress}
          placeholder="IP address"
          onChange={(event) => {
            setPage(1)
            setIpAddress(event.target.value)
          }}
        />

        <label>
          From
          <input
            type="date"
            value={dateFrom}
            max={dateTo || undefined}
            onChange={(event) => {
              setPage(1)
              setDateFrom(event.target.value)
            }}
          />
        </label>

        <label>
          To
          <input
            type="date"
            value={dateTo}
            min={dateFrom || undefined}
            onChange={(event) => {
              setPage(1)
              setDateTo(event.target.value)
            }}
          />
        </label>

        <button type="button" onClick={clearFilters}>
          Clear Filters
        </button>
      </div>

      {loading && <div className="admin-message">Loading audit logs...</div>}

      {!loading && error && (
        <div className="admin-error">
          <span>{error}</span>
          <button type="button" onClick={() => void loadLogs()}>
            Retry
          </button>
        </div>
      )}

      {!loading && !error && response && (
        <>
          <div className="admin-table-wrapper">
            <table className="admin-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>User</th>
                  <th>Action</th>
                  <th>Resource</th>
                  <th>IP Address</th>
                  <th>Details</th>
                  <th>Date</th>
                </tr>
              </thead>

              <tbody>
                {response.items.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="empty-cell">
                      No audit logs found.
                    </td>
                  </tr>
                ) : (
                  response.items.map((log) => (
                    <tr key={log.id}>
                      <td>{log.id}</td>
                      <td>{log.user_name ?? `User ${log.user_id ?? "System"}`}</td>
                      <td><code>{log.action}</code></td>
                      <td>
                        {log.resource}
                        {log.resource_id !== null && (
                          <small> #{log.resource_id}</small>
                        )}
                      </td>
                      <td>{log.ip_address ?? "—"}</td>
                      <td>
                        <details>
                          <summary>View</summary>
                          <pre>{formatDetails(log.details)}</pre>
                        </details>
                      </td>
                      <td>{formatDate(log.created_at)}</td>
                    </tr>
                  ))
                )}
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
              Page {response.page} of {Math.max(response.total_pages, 1)}
            </span>

            <button
              type="button"
              disabled={page >= response.total_pages}
              onClick={() => setPage((current) => current + 1)}
            >
              Next
            </button>
          </div>
        </>
      )}
    </div>
  )
}
