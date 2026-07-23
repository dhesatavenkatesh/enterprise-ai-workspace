import { useEffect, useState } from "react"

import {
  Activity,
  Bot,
  CheckCircle2,
  CircleAlert,
  Network,
  Workflow,
} from "lucide-react"
import { toast } from "sonner"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  getAgents,
  getApprovals,
  getMCPTools,
  getSprint4Health,
  getWorkflows,
} from "@/services/sprint4Service"
import type {
  Sprint4HealthResponse,
} from "@/types/sprint4"

interface DashboardStats {
  agents: number
  mcpTools: number
  workflows: number
  pendingApprovals: number
}

const initialStats: DashboardStats = {
  agents: 0,
  mcpTools: 0,
  workflows: 0,
  pendingApprovals: 0,
}

export function DashboardPage() {
  const [stats, setStats] =
    useState<DashboardStats>(initialStats)

  const [health, setHealth] =
    useState<Sprint4HealthResponse | null>(
      null,
    )

  const [loading, setLoading] =
    useState(true)

  useEffect(() => {
    const loadDashboardData =
      async (): Promise<void> => {
        setLoading(true)

        try {
          const [
            agentsResponse,
            mcpResponse,
            workflowsResponse,
            approvalsResponse,
            healthResponse,
          ] = await Promise.all([
            getAgents(),
            getMCPTools(),
            getWorkflows(),
            getApprovals("pending"),
            getSprint4Health(),
          ])

          setStats({
            agents:
              agentsResponse.agents?.length ??
              0,

            mcpTools:
              mcpResponse.tools?.length ??
              0,

            workflows:
              workflowsResponse.length,

            pendingApprovals:
              approvalsResponse.items
                ?.length ?? 0,
          })

          setHealth(healthResponse)
        } catch (error) {
          const message =
            error instanceof Error
              ? error.message
              : "Failed to load dashboard data"

          toast.error(message)
        } finally {
          setLoading(false)
        }
      }

    void loadDashboardData()
  }, [])

  const summaryCards = [
    {
      title: "Total Agents",
      value: stats.agents,
      description:
        "Specialized AI agents available",
      icon: Bot,
    },
    {
      title: "MCP Tools",
      value: stats.mcpTools,
      description:
        "Registered enterprise tools",
      icon: Network,
    },
    {
      title: "Workflows",
      value: stats.workflows,
      description:
        "Configured AI workflows",
      icon: Workflow,
    },
    {
      title: "Pending Approvals",
      value: stats.pendingApprovals,
      description:
        "Requests waiting for review",
      icon: CheckCircle2,
    },
  ]

  const healthModules = health
    ? [
        {
          name: "Agents",
          health: health.agents,
        },
        {
          name: "MCP Gateway",
          health: health.mcp,
        },
        {
          name: "Workflows",
          health: health.workflows,
        },
        {
          name: "Approvals",
          health: health.approvals,
        },
      ]
    : []

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">
          Dashboard
        </h1>

        <p className="mt-1 text-slate-600">
          Monitor your enterprise AI workspace.
        </p>
      </div>

      <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
        {summaryCards.map((card) => {
          const Icon = card.icon

          return (
            <Card key={card.title}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">
                  {card.title}
                </CardTitle>

                <Icon className="h-5 w-5 text-violet-600" />
              </CardHeader>

              <CardContent>
                <div className="text-3xl font-bold">
                  {loading
                    ? "..."
                    : card.value}
                </div>

                <CardDescription className="mt-2">
                  {card.description}
                </CardDescription>
              </CardContent>
            </Card>
          )
        })}
      </div>

      <Card>
        <CardHeader>
          <div className="flex items-center gap-3">
            <Activity className="h-5 w-5 text-violet-600" />

            <div>
              <CardTitle>
                Sprint 4 System Health
              </CardTitle>

              <CardDescription>
                Current availability of enterprise
                AI modules.
              </CardDescription>
            </div>
          </div>
        </CardHeader>

        <CardContent>
          {loading ? (
            <p className="text-sm text-slate-500">
              Checking system health...
            </p>
          ) : health ? (
            <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
              {healthModules.map((module) => (
                <div
                  key={module.name}
                  className="flex items-center justify-between rounded-lg border border-slate-200 p-4"
                >
                  <div>
                    <p className="font-medium text-slate-900">
                      {module.name}
                    </p>

                    <p className="mt-1 text-sm text-slate-500">
                      {module.health.message ??
                        (module.health.ready
                          ? "Module is ready"
                          : "Module is unavailable")}
                    </p>
                  </div>

                  {module.health.ready ? (
                    <CheckCircle2 className="h-5 w-5 shrink-0 text-green-600" />
                  ) : (
                    <CircleAlert className="h-5 w-5 shrink-0 text-red-600" />
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="flex items-center gap-2 text-sm text-red-600">
              <CircleAlert className="h-5 w-5" />

              <span>
                System-health information is
                unavailable.
              </span>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}