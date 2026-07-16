import { Button } from "@/components/ui/button"
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"

export function HomePage() {
  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-100 p-6">
      <Card className="w-full max-w-xl">
        <CardHeader>
          <CardTitle>
            Enterprise AI Workspace
          </CardTitle>

          <CardDescription>
            React frontend setup completed
            successfully.
          </CardDescription>
        </CardHeader>

        <CardContent>
          <Button>
            Frontend is working
          </Button>
        </CardContent>
      </Card>
    </main>
  )
}