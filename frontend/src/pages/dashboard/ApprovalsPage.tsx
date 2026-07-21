import { useEffect, useState } from "react"
import { Check, Clock3, RefreshCw, ShieldCheck, X } from "lucide-react"
import { toast } from "sonner"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { approveRequest, getApprovals, rejectRequest } from "@/services/sprint4Service"
import type { ApprovalRequest, ApprovalStatus } from "@/types/sprint4"

export function ApprovalsPage() {
  const [items, setItems] = useState<ApprovalRequest[]>([])
  const [filter, setFilter] = useState<ApprovalStatus | "all">("pending")
  const [comments, setComments] = useState<Record<string, string>>({})
  const [loading, setLoading] = useState(true)
  const [processingId, setProcessingId] = useState("")

  async function loadApprovals() {
    setLoading(true)
    try {
      const response = await getApprovals(filter === "all" ? undefined : filter)
      setItems(response.items)
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Unable to load approvals")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    void loadApprovals()
  }, [filter])

  async function decide(item: ApprovalRequest, decision: "approve" | "reject") {
    setProcessingId(item.id)
    try {
      const comment = comments[item.id] || ""
      if (decision === "approve") await approveRequest(item.id, comment)
      else await rejectRequest(item.id, comment)
      toast.success(decision === "approve" ? "Request approved" : "Request rejected")
      await loadApprovals()
    } catch (error) {
      toast.error(error instanceof Error ? error.message : "Approval action failed")
    } finally {
      setProcessingId("")
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div><h1 className="text-2xl font-bold text-slate-900">Human Approvals</h1><p className="text-sm text-slate-500">Review sensitive workflow and MCP actions.</p></div>
        <div className="flex gap-2">
          <select className="rounded-lg border bg-white px-3 text-sm" value={filter} onChange={(e) => setFilter(e.target.value as ApprovalStatus | "all")}>
            <option value="pending">Pending</option><option value="approved">Approved</option><option value="rejected">Rejected</option><option value="all">All</option>
          </select>
          <Button variant="outline" onClick={() => void loadApprovals()} disabled={loading}><RefreshCw className={loading ? "animate-spin" : ""} /> Refresh</Button>
        </div>
      </div>

      {items.length === 0 ? (
        <Card><CardContent className="flex min-h-64 flex-col items-center justify-center text-center"><ShieldCheck className="h-10 w-10 text-slate-400" /><h3 className="mt-4 font-semibold">No approval requests</h3><p className="mt-1 text-sm text-slate-500">Requests matching this filter will appear here.</p></CardContent></Card>
      ) : (
        <section className="grid gap-4 xl:grid-cols-2">
          {items.map((item) => (
            <Card key={item.id}>
              <CardHeader><div className="flex items-start justify-between gap-3"><div><CardTitle>{item.title}</CardTitle><CardDescription>{item.description}</CardDescription></div><span className="rounded-full bg-amber-100 px-2.5 py-1 text-xs font-medium text-amber-700">{item.status}</span></div></CardHeader>
              <CardContent className="space-y-4">
                <div className="grid gap-2 text-sm sm:grid-cols-2"><p><b>Type:</b> {item.resource_type}</p><p><b>Resource:</b> {item.resource_id}</p><p className="flex items-center gap-1 text-slate-500"><Clock3 className="h-4 w-4" /> {new Date(item.created_at).toLocaleString()}</p></div>
                {item.status === "pending" && <><textarea className="min-h-20 w-full rounded-xl border p-3 text-sm" placeholder="Decision comment (optional)" value={comments[item.id] || ""} onChange={(e) => setComments((current) => ({ ...current, [item.id]: e.target.value }))} /><div className="flex gap-2"><Button onClick={() => void decide(item, "approve")} disabled={processingId === item.id}><Check /> Approve</Button><Button variant="destructive" onClick={() => void decide(item, "reject")} disabled={processingId === item.id}><X /> Reject</Button></div></>}
                {item.decision_comment && <p className="rounded-lg bg-slate-50 p-3 text-sm"><b>Comment:</b> {item.decision_comment}</p>}
              </CardContent>
            </Card>
          ))}
        </section>
      )}
    </div>
  )
}
