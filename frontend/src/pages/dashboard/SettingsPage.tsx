import {
  Settings,
} from "lucide-react"

import {
  ModulePlaceholder,
} from "@/components/common/ModulePlaceholder"

export function SettingsPage() {
  return (
    <ModulePlaceholder
      title="Settings"
      description="Configure users, roles and workspace settings."
      icon={Settings}
    />
  )
}