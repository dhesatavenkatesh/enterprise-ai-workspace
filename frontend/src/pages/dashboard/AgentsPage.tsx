import {
  Bot,
} from "lucide-react"

import {
  ModulePlaceholder,
} from "@/components/common/ModulePlaceholder"

export function AgentsPage() {
  return (
    <ModulePlaceholder
      title="Agents"
      description="Create and manage specialized AI agents."
      icon={Bot}
    />
  )
}