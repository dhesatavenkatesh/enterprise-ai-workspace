import { useEffect, useState } from "react"
import { Loader2, Play, Plus, RefreshCw, Workflow } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { createWorkflow, getWorkflows, runWorkflow } from "@/services/sprint4Service"
import type { WorkflowDefinition, WorkflowStepType } from "@/types/sprint4"

export function WorkflowsPage() {
  const [workflows, setWorkflows] = useState<WorkflowDefinition[]>([])
  const [selectedId, setSelectedId] = useState("")
  const [runInput, setRunInput] = useState("")
  const [runResult, setRunResult] = useState("")
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)
  const [showCreate, setShowCreate] = useState(false)
  const [name, setName] = useState("")
  const [description, setDescription] = useState("")
  const [stepName, setStepName] = useState("Process request")
  const [stepType, setStepType] = useState<WorkflowStepType>("agent")
  const [target, setTarget] = useState("knowledge_agent")
  const [requiresApproval, setRequiresApproval] = useState(false)

  async function loadWorkflows() {
    setLoading(true)
    try {
      const response = await getWorkflows()
      setWorkflows(response)
      setSelectedId((current) => current || response[0]?.id || "")
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Unable to load workflows")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadWorkflows()
  }, [])

  async function handleCreate() {
    if (!name.trim() || !target.trim() || !stepName.trim()) {
      toast.error("Complete the workflow name, step name and target")
      return
    }
    try {
      const created = await createWorkflow({
        name: name.trim(),
        description: description.trim(),
        status: "active",
        steps: [{
          name: stepName.trim(),
          type: stepType,
          target: target.trim(),
          input_template: "{input}",
          arguments: {},
          continue_on_error: false,
          requires_approval: requiresApproval,
          approval_reason: requiresApproval ? "Human review required before execution." : null,
        }],
      })
      setWorkflows((current) => [created, ...current])
      setSelectedId(created.id)
      setShowCreate(false)
      setName("")
      setDescription("")
      toast.success("Workflow created")
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Workflow creation failed")
    }
  }

  async function handleRun() {
    if (!selectedId || !runInput.trim()) {
      toast.error("Select a workflow and enter input")
      return
    }
    setRunning(true)
    try {
      const response = await runWorkflow(selectedId, runInput.trim())
      setRunResult(JSON.stringify(response, null, 2))
      toast.success(response.status === "waiting_approval" ? "Workflow is waiting for approval" : "Workflow executed")
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Workflow execution failed")
    } finally {
      setRunning(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Workflows</h1>
          <p className="text-sm text-slate-500">Create and execute agent and MCP workflows.</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" onClick={() => void loadWorkflows()} disabled={loading}>
            <RefreshCw className={loading ? "animate-spin" : ""} /> Refresh
          </Button>
          <Button onClick={() => setShowCreate((value) => !value)}><Plus /> New workflow</Button>
        </div>
      </div>

      {showCreate && (
        <Card>
          <CardHeader><CardTitle>Create workflow</CardTitle><CardDescription>Create a one-step workflow now; more steps can be added later.</CardDescription></CardHeader>
          <CardContent className="grid gap-4 md:grid-cols-2">
            <input className="rounded-lg border p-2.5 text-sm" placeholder="Workflow name" value={name} onChange={(e) => setName(e.target.value)} />
            <input className="rounded-lg border p-2.5 text-sm" placeholder="Description" value={description} onChange={(e) => setDescription(e.target.value)} />
            <input className="rounded-lg border p-2.5 text-sm" placeholder="Step name" value={stepName} onChange={(e) => setStepName(e.target.value)} />
            <select className="rounded-lg border p-2.5 text-sm" value={stepType} onChange={(e) => setStepType(e.target.value as WorkflowStepType)}>
              <option value="agent">Agent</option><option value="mcp_tool">MCP Tool</option>
            </select>
            <input className="rounded-lg border p-2.5 text-sm" placeholder="Target name" value={target} onChange={(e) => setTarget(e.target.value)} />
            <label className="flex items-center gap-2 rounded-lg border p-2.5 text-sm"><input type="checkbox" checked={requiresApproval} onChange={(e) => setRequiresApproval(e.target.checked)} /> Require human approval</label>
            <Button className="md:col-span-2" onClick={() => void handleCreate()}><Plus /> Create workflow</Button>
          </CardContent>
        </Card>
      )}

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {workflows.map((item) => (
          <Card key={item.id} className={selectedId === item.id ? "ring-2 ring-violet-500" : ""}>
            <CardHeader><div className="mb-2 w-fit rounded-xl bg-violet-100 p-3 text-violet-600"><Workflow /></div><CardTitle>{item.name}</CardTitle><CardDescription>{item.description || "No description"}</CardDescription></CardHeader>
            <CardContent className="space-y-3"><p className="text-xs text-slate-500">{item.steps.length} step(s) · {item.status}</p><Button className="w-full" variant="outline" onClick={() => setSelectedId(item.id)}>Select</Button></CardContent>
          </Card>
        ))}
      </section>

      <Card>
        <CardHeader><CardTitle>Run selected workflow</CardTitle><CardDescription>{workflows.find((item) => item.id === selectedId)?.name || "No workflow selected"}</CardDescription></CardHeader>
        <CardContent className="space-y-4">
          <textarea className="min-h-28 w-full rounded-xl border p-3 text-sm" placeholder="Workflow input..." value={runInput} onChange={(e) => setRunInput(e.target.value)} />
          <Button onClick={() => void handleRun()} disabled={running}>{running ? <Loader2 className="animate-spin" /> : <Play />} Run workflow</Button>
          {runResult && <pre className="max-h-96 overflow-auto rounded-xl bg-slate-950 p-4 text-xs text-slate-100">{runResult}</pre>}
        </CardContent>
      </Card>
    </div>
  )
}
