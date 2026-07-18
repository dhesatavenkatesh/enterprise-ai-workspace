import {
  Workflow,
} from "lucide-react"

import {
  ModulePlaceholder,
} from "@/components/common/ModulePlaceholder"

export function WorkflowsPage() {
  return (
    <ModulePlaceholder
      title="Workflows"
      description="Build automated enterprise AI workflows."
      icon={Workflow}
    />
  )
}