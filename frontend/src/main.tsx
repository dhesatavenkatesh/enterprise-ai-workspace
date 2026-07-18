import {
  StrictMode,
} from "react"

import {
  createRoot,
} from "react-dom/client"

import {
  QueryClientProvider,
} from "@tanstack/react-query"

import {
  BrowserRouter,
} from "react-router-dom"

import {
  AuthInitializer,
} from "@/components/common/AuthInitializer"

import {
  GlobalAuthHandler,
} from "@/components/common/GlobalAuthHandler"

import {
  Toaster,
} from "@/components/ui/sonner"

import {
  queryClient,
} from "@/lib/queryClient"

import App from "./App"
import "./index.css"

const rootElement =
  document.getElementById("root")

if (!rootElement) {
  throw new Error(
    "Root element was not found",
  )
}

createRoot(rootElement).render(
  <StrictMode>
    <QueryClientProvider
      client={queryClient}
    >
      <BrowserRouter>
        <GlobalAuthHandler>
          <AuthInitializer>
            <App />
          </AuthInitializer>
        </GlobalAuthHandler>

        <Toaster richColors />
      </BrowserRouter>
    </QueryClientProvider>
  </StrictMode>,
)