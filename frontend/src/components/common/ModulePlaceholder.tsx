import type {
  LucideIcon,
} from "lucide-react"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

interface ModulePlaceholderProps {
  title: string
  description: string
  icon: LucideIcon
}

export function ModulePlaceholder({
  title,
  description,
  icon: Icon,
}: ModulePlaceholderProps) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-slate-900">
          {title}
        </h2>

        <p className="mt-1 text-slate-500">
          {description}
        </p>
      </div>

      <Card>
        <CardHeader>
          <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-violet-100 text-violet-600">
            <Icon className="h-6 w-6" />
          </div>

          <CardTitle>
            {title}
          </CardTitle>

          <CardDescription>
            This module is prepared for a
            future sprint.
          </CardDescription>
        </CardHeader>

        <CardContent>
          <div className="flex min-h-72 items-center justify-center rounded-xl border border-dashed bg-slate-50">
            <div className="max-w-md p-6 text-center">
              <p className="text-lg font-semibold text-slate-800">
                Coming soon
              </p>

              <p className="mt-2 text-sm text-slate-500">
                Backend APIs and AI
                capabilities will be
                connected in the next
                development phase.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}