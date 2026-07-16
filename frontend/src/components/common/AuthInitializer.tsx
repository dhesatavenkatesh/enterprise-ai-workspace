import {
  useEffect,
  useRef,
} from "react"

import type {
  ReactNode,
} from "react"

import {
  authService,
} from "@/services/authService"

import {
  useAuthStore,
} from "@/store/authStore"

import {
  tokenStorage,
} from "@/utils/tokenStorage"

interface AuthInitializerProps {
  children: ReactNode
}

export function AuthInitializer({
  children,
}: AuthInitializerProps) {
  const initialized =
    useRef(false)

  const {
    setUser,
    clearAuth,
    setInitializing,
  } = useAuthStore()

  useEffect(() => {
    if (initialized.current) {
      return
    }

    initialized.current = true

    async function initializeAuth() {
      const accessToken =
        tokenStorage.getAccessToken()

      const refreshToken =
        tokenStorage.getRefreshToken()

      if (
        !accessToken &&
        !refreshToken
      ) {
        clearAuth()
        setInitializing(false)

        return
      }

      try {
        const user =
          await authService.getMe()

        setUser(user)
      } catch {
        /*
         * The Axios interceptor attempts
         * token refresh automatically.
         *
         * If refresh also fails, tokens
         * are already removed.
         */
        clearAuth()
      } finally {
        setInitializing(false)
      }
    }

    void initializeAuth()
  }, [
    clearAuth,
    setInitializing,
    setUser,
  ])

  return children
}