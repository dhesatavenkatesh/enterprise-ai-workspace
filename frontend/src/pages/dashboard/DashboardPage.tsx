import {
  Activity,
  Bot,
  BrainCircuit,
  Database,
  TrendingUp,
  Users,
} from "lucide-react"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

import {
  useAuthStore,
} from "@/store/authStore"

const statistics = [
  {
    title: "AI Conversations",
    value: "0",
    description:
      "Conversations this month",
    icon: BrainCircuit,
  },
  {
    title: "Knowledge Documents",
    value: "0",
    description:
      "Indexed documents",
    icon: Database,
  },
  {
    title: "Active Agents",
    value: "0",
    description:
      "Configured AI agents",
    icon: Bot,
  },
  {
    title: "Team Members",
    value: "5",
    description:
      "Workspace members",
    icon: Users,
  },
]

export function DashboardPage() {
  const user = useAuthStore(
    (state) => state.user,
  )

  return (
    <div className="space-y-6">
      <section className="rounded-2xl bg-gradient-to-r from-violet-600 to-indigo-600 p-6 text-white shadow-lg">
        <p className="text-sm font-medium text-violet-100">
          Enterprise AI Workspace
        </p>

        <h2 className="mt-2 text-2xl font-bold md:text-3xl">
          Welcome back, {user?.name}
        </h2>

        <p className="mt-2 max-w-2xl text-sm text-violet-100 md:text-base">
          Manage AI conversations,
          knowledge, agents, workflows and
          analytics from your secure
          workspace.
        </p>

        <div className="mt-5 inline-flex items-center gap-2 rounded-full bg-white/15 px-3 py-1.5 text-sm">
          <Activity className="h-4 w-4" />
          Account status:{" "}
          {user?.status}
        </div>
      </section>

      <section className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {statistics.map((item) => {
          const Icon = item.icon

          return (
            <Card key={item.title}>
              <CardContent className="flex items-start justify-between p-5">
                <div>
                  <p className="text-sm text-slate-500">
                    {item.title}
                  </p>

                  <p className="mt-2 text-3xl font-bold text-slate-900">
                    {item.value}
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    {item.description}
                  </p>
                </div>

                <div className="rounded-xl bg-violet-100 p-3 text-violet-600">
                  <Icon className="h-5 w-5" />
                </div>
              </CardContent>
            </Card>
          )
        })}
      </section>

      <section className="grid gap-6 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader>
            <CardTitle>
              Workspace activity
            </CardTitle>

            <CardDescription>
              Recent activity will appear
              here.
            </CardDescription>
          </CardHeader>

          <CardContent>
            <div className="flex min-h-64 flex-col items-center justify-center rounded-xl border border-dashed bg-slate-50 p-6 text-center">
              <TrendingUp className="h-10 w-10 text-slate-400" />

              <h3 className="mt-4 font-semibold">
                No activity available
              </h3>

              <p className="mt-1 max-w-sm text-sm text-slate-500">
                Activity analytics will be
                displayed after AI modules
                are connected.
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>
              Your profile
            </CardTitle>

            <CardDescription>
              Current account information
            </CardDescription>
          </CardHeader>

          <CardContent className="space-y-4">
            <ProfileRow
              label="Name"
              value={user?.name ?? "-"}
            />

            <ProfileRow
              label="Email"
              value={user?.email ?? "-"}
            />

            <ProfileRow
              label="Role"
              value={user?.role ?? "-"}
            />

            <ProfileRow
              label="Status"
              value={user?.status ?? "-"}
            />
          </CardContent>
        </Card>
      </section>
    </div>
  )
}

interface ProfileRowProps {
  label: string
  value: string
}

function ProfileRow({
  label,
  value,
}: ProfileRowProps) {
  return (
    <div className="border-b pb-3 last:border-0 last:pb-0">
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </p>

      <p className="mt-1 break-words text-sm font-medium text-slate-900">
        {value}
      </p>
    </div>
  )
}