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

interface AuthInitializerProps {
  children: ReactNode
}

export function AuthInitializer({
  children,
}: AuthInitializerProps) {
  const initialized =
    useRef(false)

  const setUser =
    useAuthStore(
      (state) => state.setUser,
    )

  const clearAuth =
    useAuthStore(
      (state) => state.clearAuth,
    )

  const setInitializing =
    useAuthStore(
      (state) =>
        state.setInitializing,
    )

  useEffect(() => {
    if (initialized.current) {
      return
    }

    initialized.current = true

    async function initializeAuth():
      Promise<void> {
      setInitializing(true)

      const accessToken =
        localStorage.getItem(
          "access_token",
        )

      const refreshToken =
        localStorage.getItem(
          "refresh_token",
        )

      if (
        !accessToken &&
        !refreshToken
      ) {
        clearAuth()
        return
      }

      try {
        const user =
          await authService.getMe()

        setUser(user)
      } catch (error) {
        console.error(
          "Authentication initialization failed:",
          error,
        )

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