import {
  useCallback,
  useEffect,
  useState,
} from "react"

import {
  Activity,
  Bot,
  CheckCircle2,
  Clock3,
  Coins,
  RefreshCw,
  XCircle,
} from "lucide-react"
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Legend,
  Line,
  LineChart,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  getAgentAnalytics,
} from "@/services/agentAnalyticsService"
import type {
  AgentAnalyticsResponse,
} from "@/types/agentAnalytics"

const PIE_COLORS = [
  "#16a34a",
  "#dc2626",
]

export function AgentAnalyticsPage() {
  const [
    analytics,
    setAnalytics,
  ] =
    useState<AgentAnalyticsResponse | null>(
      null,
    )

  const [loading, setLoading] =
    useState(true)

  const [days, setDays] =
    useState(7)

  const loadAnalytics =
    useCallback(async (): Promise<void> => {
      setLoading(true)

      try {
        const response =
          await getAgentAnalytics(days)

        setAnalytics(response)
      } catch (error) {
        const message =
          error instanceof Error
            ? error.message
            : "Failed to load agent analytics"

        toast.error(message)
      } finally {
        setLoading(false)
      }
    }, [days])

  useEffect(() => {
    void loadAnalytics()
  }, [loadAnalytics])

  const summary = analytics?.summary

  const executionPieData = [
    {
      name: "Successful",
      value:
        summary?.successful_runs ?? 0,
    },
    {
      name: "Failed",
      value:
        summary?.failed_runs ?? 0,
    },
  ]

  const summaryCards = [
    {
      title: "Total Executions",
      value:
        summary?.total_executions ?? 0,
      description:
        "All recorded agent runs",
      icon: Activity,
    },
    {
      title: "Successful Runs",
      value:
        summary?.successful_runs ?? 0,
      description: `${
        summary?.success_rate ?? 0
      }% success rate`,
      icon: CheckCircle2,
    },
    {
      title: "Failed Runs",
      value:
        summary?.failed_runs ?? 0,
      description:
        "Executions requiring attention",
      icon: XCircle,
    },
    {
      title: "Average Response",
      value: `${
        summary?.average_response_time_ms ??
        0
      } ms`,
      description:
        "Average agent response time",
      icon: Clock3,
    },
    {
      title: "Token Usage",
      value:
        summary?.total_tokens ?? 0,
      description:
        "Combined input and output tokens",
      icon: Coins,
    },
    {
      title: "Workflow Duration",
      value: `${
        summary
          ?.average_workflow_duration_ms ??
        0
      } ms`,
      description:
        "Average workflow execution time",
      icon: Bot,
    },
  ]

  return (
    <div className="space-y-8">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">
            Agent Analytics
          </h1>

          <p className="mt-1 text-slate-600">
            Monitor agent performance,
            reliability, token usage and tool
            activity.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={days}
            onChange={(event) =>
              setDays(
                Number(event.target.value),
              )
            }
            className="h-10 rounded-md border border-slate-300 bg-white px-3 text-sm"
          >
            <option value={7}>
              Last 7 days
            </option>

            <option value={30}>
              Last 30 days
            </option>

            <option value={90}>
              Last 90 days
            </option>
          </select>

          <Button
            variant="outline"
            onClick={() =>
              void loadAnalytics()
            }
            disabled={loading}
          >
            <RefreshCw
              className={`h-4 w-4 ${
                loading
                  ? "animate-spin"
                  : ""
              }`}
            />

            Refresh
          </Button>
        </div>
      </div>

      <div className="grid gap-5 sm:grid-cols-2 xl:grid-cols-3">
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

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>
              Execution Trend
            </CardTitle>

            <CardDescription>
              Successful and failed agent runs
              over time.
            </CardDescription>
          </CardHeader>

          <CardContent className="h-[340px]">
            <ResponsiveContainer
              width="100%"
              height="100%"
            >
              <LineChart
                data={
                  analytics?.trends ?? []
                }
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                />

                <XAxis
                  dataKey="date"
                  tickFormatter={(value) =>
                    new Date(
                      value,
                    ).toLocaleDateString(
                      undefined,
                      {
                        month: "short",
                        day: "numeric",
                      },
                    )
                  }
                />

                <YAxis />

                <Tooltip />

                <Legend />

                <Line
                  type="monotone"
                  dataKey="successful_runs"
                  name="Successful"
                  stroke="#16a34a"
                  strokeWidth={2}
                />

                <Line
                  type="monotone"
                  dataKey="failed_runs"
                  name="Failed"
                  stroke="#dc2626"
                  strokeWidth={2}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>
              Execution Status
            </CardTitle>

            <CardDescription>
              Distribution of successful and
              failed agent runs.
            </CardDescription>
          </CardHeader>

          <CardContent className="h-[340px]">
            <ResponsiveContainer
              width="100%"
              height="100%"
            >
              <PieChart>
                <Pie
                  data={executionPieData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={105}
                  label
                >
                  {executionPieData.map(
                    (_, index) => (
                      <Cell
                        key={`status-${index}`}
                        fill={
                          PIE_COLORS[
                            index %
                              PIE_COLORS.length
                          ]
                        }
                      />
                    ),
                  )}
                </Pie>

                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 xl:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>
              Tool Usage
            </CardTitle>

            <CardDescription>
              Most frequently used MCP tools.
            </CardDescription>
          </CardHeader>

          <CardContent className="h-[340px]">
            <ResponsiveContainer
              width="100%"
              height="100%"
            >
              <BarChart
                data={
                  analytics?.tool_usage ?? []
                }
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                />

                <XAxis
                  dataKey="tool_name"
                  interval={0}
                  angle={-20}
                  textAnchor="end"
                  height={80}
                />

                <YAxis />

                <Tooltip />

                <Bar
                  dataKey="usage_count"
                  name="Usage"
                  fill="#7c3aed"
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>
              Token Usage Trend
            </CardTitle>

            <CardDescription>
              Daily token consumption by all
              agents.
            </CardDescription>
          </CardHeader>

          <CardContent className="h-[340px]">
            <ResponsiveContainer
              width="100%"
              height="100%"
            >
              <BarChart
                data={
                  analytics?.trends ?? []
                }
              >
                <CartesianGrid
                  strokeDasharray="3 3"
                />

                <XAxis
                  dataKey="date"
                  tickFormatter={(value) =>
                    new Date(
                      value,
                    ).toLocaleDateString(
                      undefined,
                      {
                        month: "short",
                        day: "numeric",
                      },
                    )
                  }
                />

                <YAxis />

                <Tooltip />

                <Bar
                  dataKey="token_usage"
                  name="Tokens"
                  fill="#2563eb"
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>
            Agent Leaderboard
          </CardTitle>

          <CardDescription>
            Agent ranking based on success rate
            and execution count.
          </CardDescription>
        </CardHeader>

        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full min-w-[800px] text-left text-sm">
              <thead>
                <tr className="border-b text-slate-500">
                  <th className="px-3 py-3">
                    Rank
                  </th>

                  <th className="px-3 py-3">
                    Agent
                  </th>

                  <th className="px-3 py-3">
                    Executions
                  </th>

                  <th className="px-3 py-3">
                    Success
                  </th>

                  <th className="px-3 py-3">
                    Failed
                  </th>

                  <th className="px-3 py-3">
                    Success Rate
                  </th>

                  <th className="px-3 py-3">
                    Avg. Response
                  </th>

                  <th className="px-3 py-3">
                    Tokens
                  </th>
                </tr>
              </thead>

              <tbody>
                {analytics?.leaderboard.map(
                  (agent) => (
                    <tr
                      key={agent.agent_name}
                      className="border-b last:border-0"
                    >
                      <td className="px-3 py-4 font-semibold">
                        #{agent.rank}
                      </td>

                      <td className="px-3 py-4 font-medium">
                        {agent.agent_name}
                      </td>

                      <td className="px-3 py-4">
                        {
                          agent.total_executions
                        }
                      </td>

                      <td className="px-3 py-4 text-green-700">
                        {
                          agent.successful_runs
                        }
                      </td>

                      <td className="px-3 py-4 text-red-700">
                        {agent.failed_runs}
                      </td>

                      <td className="px-3 py-4">
                        {agent.success_rate}%
                      </td>

                      <td className="px-3 py-4">
                        {
                          agent.average_response_time_ms
                        }{" "}
                        ms
                      </td>

                      <td className="px-3 py-4">
                        {agent.token_usage}
                      </td>
                    </tr>
                  ),
                )}

                {!loading &&
                  !analytics?.leaderboard
                    .length && (
                    <tr>
                      <td
                        colSpan={8}
                        className="px-3 py-10 text-center text-slate-500"
                      >
                        No agent execution
                        metrics are available.
                      </td>
                    </tr>
                  )}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}