import {
  LoaderCircle,
} from "lucide-react"

interface LoadingScreenProps {
  message?: string
}

export function LoadingScreen({
  message = "Loading...",
}: LoadingScreenProps) {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center gap-4 bg-slate-100">
      <LoaderCircle className="h-10 w-10 animate-spin text-slate-900" />

      <p className="text-sm text-slate-600">
        {message}
      </p>
    </main>
  )
}