import {
  useEffect,
} from "react"

import type {
  ReactNode,
} from "react"

import {
  useLocation,
  useNavigate,
} from "react-router-dom"

import {
  toast,
} from "sonner"

import {
  queryClient,
} from "@/lib/queryClient"

import {
  useAuthStore,
} from "@/store/authStore"

import {
  registerForbiddenHandler,
  registerUnauthorizedHandler,
} from "@/utils/authEvents"

interface GlobalAuthHandlerProps {
  children: ReactNode
}

export function GlobalAuthHandler({
  children,
}: GlobalAuthHandlerProps) {
  const navigate = useNavigate()
  const location = useLocation()

  const clearAuth =
    useAuthStore(
      (state) => state.clearAuth,
    )

  useEffect(() => {
    const unregisterUnauthorized =
      registerUnauthorizedHandler(
        () => {
          clearAuth()
          queryClient.clear()

          toast.error(
            "Your session has expired. Please sign in again.",
          )

          navigate("/login", {
            replace: true,
            state: {
              from: location,
            },
          })
        },
      )

    const unregisterForbidden =
      registerForbiddenHandler(
        () => {
          toast.error(
            "Permission Denied",
          )

          navigate(
            "/unauthorized",
            {
              replace: true,
            },
          )
        },
      )

    return () => {
      unregisterUnauthorized()
      unregisterForbidden()
    }
  }, [
    clearAuth,
    location,
    navigate,
  ])

  return children
}