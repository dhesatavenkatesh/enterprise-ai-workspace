import {
  useState,
} from "react"

import {
  Bot,
  LoaderCircle,
  Play,
  Wrench,
} from "lucide-react"

import {
  Button,
} from "@/components/ui/button"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

import {
  orchestratorService,
  type OrchestratorResponse,
} from "@/services/orchestratorService"

export function OrchestratorPage() {
  const [query, setQuery] =
    useState("")

  const [result, setResult] =
    useState<OrchestratorResponse | null>(
      null,
    )

  const [isExecuting, setIsExecuting] =
    useState(false)

  const [errorMessage, setErrorMessage] =
    useState("")

  const executeRequest =
    async (): Promise<void> => {
      const normalizedQuery =
        query.trim()

      if (
        normalizedQuery.length < 2
      ) {
        setErrorMessage(
          "Please enter a valid request.",
        )
        return
      }

      setIsExecuting(true)
      setResult(null)
      setErrorMessage("")

      try {
        const response =
          await orchestratorService.execute({
            query: normalizedQuery,
          })

        setResult(response)
      } catch (error) {
        console.error(
          "Orchestrator execution failed:",
          error,
        )

        setErrorMessage(
          "Unable to execute the request. Check whether the backend is running and the orchestrator endpoint is available.",
        )
      } finally {
        setIsExecuting(false)
      }
    }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900">
          Multi-Agent Orchestrator
        </h1>

        <p className="mt-2 text-slate-600">
          Submit a request and let the
          orchestrator select the correct
          enterprise agent and tools.
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>
            Execute request
          </CardTitle>

          <CardDescription>
            The orchestrator analyses your
            request and routes it to the
            most suitable agent.
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          <textarea
            value={query}
            onChange={(event) => {
              setQuery(event.target.value)

              if (errorMessage) {
                setErrorMessage("")
              }
            }}
            placeholder="Example: What is the employee leave policy?"
            rows={6}
            disabled={isExecuting}
            className="w-full resize-none rounded-lg border border-slate-300 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-violet-500 focus:ring-2 focus:ring-violet-200 disabled:cursor-not-allowed disabled:bg-slate-100"
          />

          {errorMessage && (
            <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
              {errorMessage}
            </div>
          )}

          <Button
            type="button"
            onClick={() => {
              void executeRequest()
            }}
            disabled={
              isExecuting ||
              query.trim().length < 2
            }
            className="gap-2"
          >
            {isExecuting ? (
              <>
                <LoaderCircle className="h-4 w-4 animate-spin" />
                Executing...
              </>
            ) : (
              <>
                <Play className="h-4 w-4" />
                Run orchestrator
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {result && (
        <div className="grid gap-6 lg:grid-cols-3">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bot className="h-5 w-5" />
                Selected agent
              </CardTitle>
            </CardHeader>

            <CardContent className="space-y-2">
              <p className="text-lg font-semibold text-slate-900">
                {result.agent}
              </p>

              <p className="text-sm text-slate-600">
                Status:{" "}
                <span className="font-medium">
                  {result.status}
                </span>
              </p>

              <p className="text-sm text-slate-600">
                Duration:{" "}
                {Number(
                  result.duration_ms,
                ).toFixed(2)}{" "}
                ms
              </p>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Wrench className="h-5 w-5" />
                Selected tools
              </CardTitle>
            </CardHeader>

            <CardContent>
              {result.tools &&
              result.tools.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {result.tools.map(
                    (tool) => (
                      <span
                        key={tool}
                        className="rounded-full bg-violet-100 px-3 py-1 text-sm font-medium text-violet-700"
                      >
                        {tool}
                      </span>
                    ),
                  )}
                </div>
              ) : (
                <p className="text-sm text-slate-600">
                  No external tools were
                  selected.
                </p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>
                User request
              </CardTitle>
            </CardHeader>

            <CardContent>
              <p className="whitespace-pre-wrap text-sm text-slate-700">
                {result.query}
              </p>
            </CardContent>
          </Card>

          <Card className="lg:col-span-3">
            <CardHeader>
              <CardTitle>
                Agent response
              </CardTitle>
            </CardHeader>

            <CardContent>
              <p className="whitespace-pre-wrap text-slate-700">
                {result.answer}
              </p>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}