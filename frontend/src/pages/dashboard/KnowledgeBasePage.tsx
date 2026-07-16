import {
  Database,
} from "lucide-react"

import {
  ModulePlaceholder,
} from "@/components/common/ModulePlaceholder"

export function KnowledgeBasePage() {
  return (
    <ModulePlaceholder
      title="Knowledge Base"
      description="Upload, search and manage enterprise documents."
      icon={Database}
    />
  )
}