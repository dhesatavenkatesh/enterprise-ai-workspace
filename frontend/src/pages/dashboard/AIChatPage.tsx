import {
  BrainCircuit,
} from "lucide-react"

import {
  ModulePlaceholder,
} from "@/components/common/ModulePlaceholder"

export function AIChatPage() {
  return (
    <ModulePlaceholder
      title="AI Chat"
      description="Chat with secure enterprise AI assistants."
      icon={BrainCircuit}
    />
  )
}