import { useEffect, useState } from "react"
import { Loader2, Play, PlugZap, RefreshCw } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { callMCPTool, getMCPTools } from "@/services/sprint4Service"
import type { MCPToolDefinition } from "@/types/sprint4"

export function MCPToolsPage() {
  const [tools, setTools] = useState<MCPToolDefinition[]>([])
  const [selected, setSelected] = useState<MCPToolDefinition | null>(null)
  const [argumentsText, setArgumentsText] = useState("{}")
  const [result, setResult] = useState("")
  const [loading, setLoading] = useState(true)
  const [executing, setExecuting] = useState(false)

  async function loadTools() {
    setLoading(true)
    try {
      const response = await getMCPTools()
      setTools(response.tools)
      setSelected((current) => current || response.tools[0] || null)
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Unable to load MCP tools")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadTools()
  }, [])

  async function handleCall() {
    if (!selected) return
    let args: Record<string, unknown>
    try {
      args = JSON.parse(argumentsText) as Record<string, unknown>
    } catch {
      toast.error("Arguments must be valid JSON")
      return
    }

    setExecuting(true)
    try {
      const response = await callMCPTool(selected.name, args)
      setResult(JSON.stringify(response, null, 2))
      toast.success("MCP tool executed")
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Tool execution failed")
    } finally {
      setExecuting(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">MCP Tools</h1>
          <p className="text-sm text-slate-500">Discover and execute registered MCP tools.</p>
        </div>
        <Button variant="outline" onClick={() => void loadTools()} disabled={loading}>
          <RefreshCw className={loading ? "animate-spin" : ""} /> Refresh
        </Button>
      </div>

      <div className="grid gap-6 xl:grid-cols-3">
        <section className="grid gap-4 sm:grid-cols-2 xl:col-span-2">
          {tools.map((tool) => (
            <Card key={tool.name} className={selected?.name === tool.name ? "ring-2 ring-violet-500" : ""}>
              <CardHeader>
                <div className="mb-2 w-fit rounded-xl bg-indigo-100 p-3 text-indigo-600"><PlugZap /></div>
                <CardTitle>{tool.name}</CardTitle>
                <CardDescription>{tool.description}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-xs text-slate-500">Category: {tool.category}</p>
                <Button className="w-full" variant="outline" onClick={() => setSelected(tool)}>Configure</Button>
              </CardContent>
            </Card>
          ))}
        </section>

        <Card>
          <CardHeader>
            <CardTitle>Execute tool</CardTitle>
            <CardDescription>{selected?.name || "Select a tool"}</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <textarea
              className="min-h-40 w-full rounded-xl border bg-slate-950 p-3 font-mono text-sm text-slate-100 outline-none focus:ring-2 focus:ring-violet-500"
              value={argumentsText}
              onChange={(event) => setArgumentsText(event.target.value)}
            />
            <Button className="w-full" onClick={() => void handleCall()} disabled={!selected || executing}>
              {executing ? <Loader2 className="animate-spin" /> : <Play />} Execute
            </Button>
            {result && <pre className="max-h-80 overflow-auto rounded-xl bg-slate-950 p-3 text-xs text-slate-100">{result}</pre>}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
