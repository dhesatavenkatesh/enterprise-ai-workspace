import {
  Mail,
  Shield,
  User,
} from "lucide-react"

import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

import {
  useAuthStore,
} from "@/store/authStore"

export function ProfilePage() {
  const user = useAuthStore(
    (state) => state.user,
  )

  const initial =
    user?.name
      .trim()
      .charAt(0)
      .toUpperCase() ?? "U"

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div>
        <h2 className="text-2xl font-bold">
          Profile
        </h2>

        <p className="text-slate-500">
          View your workspace account
          information.
        </p>
      </div>

      <Card>
        <CardHeader className="items-center text-center">
          <div className="flex h-24 w-24 items-center justify-center rounded-full bg-violet-600 text-3xl font-bold text-white">
            {initial}
          </div>

          <CardTitle className="mt-3 text-2xl">
            {user?.name}
          </CardTitle>

          <p className="text-sm text-slate-500">
            {user?.role}
          </p>
        </CardHeader>

        <CardContent className="space-y-4">
          <ProfileItem
            icon={User}
            label="Full name"
            value={user?.name ?? "-"}
          />

          <ProfileItem
            icon={Mail}
            label="Email address"
            value={user?.email ?? "-"}
          />

          <ProfileItem
            icon={Shield}
            label="Account status"
            value={user?.status ?? "-"}
          />
        </CardContent>
      </Card>
    </div>
  )
}

interface ProfileItemProps {
  icon: typeof User
  label: string
  value: string
}

function ProfileItem({
  icon: Icon,
  label,
  value,
}: ProfileItemProps) {
  return (
    <div className="flex items-center gap-4 rounded-xl border p-4">
      <div className="rounded-lg bg-slate-100 p-3 text-slate-600">
        <Icon className="h-5 w-5" />
      </div>

      <div className="min-w-0">
        <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
          {label}
        </p>

        <p className="truncate font-medium">
          {value}
        </p>
      </div>
    </div>
  )
}