import {
  BrainCircuit,
  ShieldCheck,
  Sparkles,
} from "lucide-react"

import {
  Outlet,
} from "react-router-dom"

export function AuthLayout() {
  return (
    <main className="grid min-h-screen bg-slate-100 lg:grid-cols-2">
      <section className="hidden bg-slate-950 p-12 text-white lg:flex lg:flex-col lg:justify-between">
        <div className="flex items-center gap-3">
          <div className="rounded-xl bg-white/10 p-3">
            <BrainCircuit className="h-7 w-7" />
          </div>

          <div>
            <h1 className="text-xl font-semibold">
              Enterprise AI Workspace
            </h1>

            <p className="text-sm text-slate-400">
              Secure enterprise intelligence
            </p>
          </div>
        </div>

        <div className="space-y-8">
          <div>
            <h2 className="max-w-xl text-4xl font-bold leading-tight">
              Work smarter with secure,
              role-based AI tools.
            </h2>

            <p className="mt-4 max-w-lg text-slate-300">
              Access AI chat, knowledge,
              workflows, agents and analytics
              from a single enterprise workspace.
            </p>
          </div>

          <div className="grid gap-4">
            <div className="flex items-start gap-3">
              <ShieldCheck className="mt-1 h-5 w-5 text-emerald-400" />

              <div>
                <p className="font-medium">
                  Enterprise security
                </p>

                <p className="text-sm text-slate-400">
                  JWT authentication and
                  role-based access control.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <Sparkles className="mt-1 h-5 w-5 text-violet-400" />

              <div>
                <p className="font-medium">
                  AI productivity
                </p>

                <p className="text-sm text-slate-400">
                  Intelligent tools for every
                  team and department.
                </p>
              </div>
            </div>
          </div>
        </div>

        <p className="text-sm text-slate-500">
          © 2026 Enterprise AI Workspace
        </p>
      </section>

      <section className="flex items-center justify-center p-6 md:p-10">
        <div className="w-full max-w-md">
          <Outlet />
        </div>
      </section>
    </main>
  )
}