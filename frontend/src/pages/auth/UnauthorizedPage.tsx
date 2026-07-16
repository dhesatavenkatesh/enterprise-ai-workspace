import {
  ShieldX,
} from "lucide-react"

import {
  Link,
} from "react-router-dom"

import {
  buttonVariants,
} from "@/components/ui/button"

import {
  cn,
} from "@/lib/utils"

export function UnauthorizedPage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-100 p-6">
      <div className="max-w-lg text-center">
        <div className="mx-auto flex h-20 w-20 items-center justify-center rounded-full bg-red-100">
          <ShieldX className="h-10 w-10 text-red-600" />
        </div>

        <h1 className="mt-6 text-4xl font-bold">
          Permission denied
        </h1>

        <p className="mt-3 text-slate-600">
          Your current role does not have
          permission to access this page.
        </p>

        <Link
          to="/dashboard"
          className={cn(
            buttonVariants(),
            "mt-6",
          )}
        >
          Return to dashboard
        </Link>
      </div>
    </main>
  )
}