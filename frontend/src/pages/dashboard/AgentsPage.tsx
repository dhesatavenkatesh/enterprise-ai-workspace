import { useEffect, useState } from "react"
import { Bot, Loader2, Play, RefreshCw } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import { executeAgent, getAgents } from "@/services/sprint4Service"
import type { AgentDefinition } from "@/types/sprint4"

export function AgentsPage() {
  const [agents, setAgents] = useState<AgentDefinition[]>([])
  const [selectedAgent, setSelectedAgent] = useState("")
  const [message, setMessage] = useState("")
  const [result, setResult] = useState("")
  const [loading, setLoading] = useState(true)
  const [executing, setExecuting] = useState(false)

  async function loadAgents() {
    setLoading(true)
    try {
      const response = await getAgents()
      setAgents(response.agents)
      setSelectedAgent((current) => current || response.agents[0]?.name || "")
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Unable to load agents")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadAgents()
  }, [])

  async function handleExecute() {
    if (!selectedAgent || !message.trim()) {
      toast.error("Select an agent and enter a message")
      return
    }

    setExecuting(true)
    setResult("")
    try {
      const response = await executeAgent({
        message: message.trim(),
        agent_name: selectedAgent,
      })
      setResult(response.final_answer)
      toast.success("Agent completed successfully")
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Agent execution failed")
    } finally {
      setExecuting(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">AI Agents</h1>
          <p className="text-sm text-slate-500">Run specialized enterprise agents.</p>
        </div>
        <Button variant="outline" onClick={() => void loadAgents()} disabled={loading}>
          <RefreshCw className={loading ? "animate-spin" : ""} /> Refresh
        </Button>
      </div>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {agents.map((agent) => (
          <Card
            key={agent.name}
            className={selectedAgent === agent.name ? "ring-2 ring-violet-500" : ""}
          >
            <CardHeader>
              <div className="mb-2 w-fit rounded-xl bg-violet-100 p-3 text-violet-600">
                <Bot className="h-5 w-5" />
              </div>
              <CardTitle>{agent.name}</CardTitle>
              <CardDescription>
                {agent.description || "Specialized enterprise AI agent"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button
                className="w-full"
                variant={selectedAgent === agent.name ? "default" : "outline"}
                onClick={() => setSelectedAgent(agent.name)}
              >
                Select agent
              </Button>
            </CardContent>
          </Card>
        ))}
      </section>

      <Card>
        <CardHeader>
          <CardTitle>Execute agent</CardTitle>
          <CardDescription>Selected: {selectedAgent || "None"}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <textarea
            className="min-h-32 w-full rounded-xl border bg-white p-3 text-sm outline-none focus:ring-2 focus:ring-violet-500"
            placeholder="Enter a task for the selected agent..."
            value={message}
            onChange={(event) => setMessage(event.target.value)}
          />
          <Button onClick={() => void handleExecute()} disabled={executing}>
            {executing ? <Loader2 className="animate-spin" /> : <Play />}
            Run agent
          </Button>
          {result && (
            <div className="whitespace-pre-wrap rounded-xl border bg-slate-50 p-4 text-sm text-slate-700">
              {result}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
