import { Link } from "react-router-dom"

import { buttonVariants } from "@/components/ui/button"
import { cn } from "@/lib/utils"

export function NotFoundPage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 bg-slate-100 p-6">
      <h1 className="text-6xl font-bold text-slate-900">
        404
      </h1>

      <p className="text-slate-600">
        Page not found
      </p>

      <Link
        to="/"
        className={cn(
          buttonVariants({
            variant: "default",
          }),
        )}
      >
        Return Home
      </Link>
    </main>
  )
}