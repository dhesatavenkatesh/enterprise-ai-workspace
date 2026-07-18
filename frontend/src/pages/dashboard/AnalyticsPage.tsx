import {
  BarChart3,
} from "lucide-react"

import {
  ModulePlaceholder,
} from "@/components/common/ModulePlaceholder"

export function AnalyticsPage() {
  return (
    <ModulePlaceholder
      title="Analytics"
      description="Monitor workspace usage and AI performance."
      icon={BarChart3}
    />
  )
}