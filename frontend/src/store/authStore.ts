import { create } from "zustand"

import type {
  AuthUser,
} from "@/types/auth"

interface AuthState {
  user: AuthUser | null
  accessToken: string | null
  refreshToken: string | null
  isAuthenticated: boolean
  isInitializing: boolean

  setAuth: (
    user: AuthUser,
    accessToken: string,
    refreshToken: string,
  ) => void

  setUser: (
    user: AuthUser | null,
  ) => void

  setInitializing: (
    isInitializing: boolean,
  ) => void

  clearAuth: () => void

  logout: () => void
}

const ACCESS_TOKEN_KEY =
  "access_token"

const REFRESH_TOKEN_KEY =
  "refresh_token"

const USER_KEY =
  "auth_user"

function readStoredUser():
  AuthUser | null {
  const storedUser =
    localStorage.getItem(
      USER_KEY,
    )

  if (!storedUser) {
    return null
  }

  try {
    return JSON.parse(
      storedUser,
    ) as AuthUser
  } catch {
    localStorage.removeItem(
      USER_KEY,
    )

    return null
  }
}

function clearStoredAuth(): void {
  localStorage.removeItem(
    ACCESS_TOKEN_KEY,
  )

  localStorage.removeItem(
    REFRESH_TOKEN_KEY,
  )

  localStorage.removeItem(
    USER_KEY,
  )
}

const initialAccessToken =
  localStorage.getItem(
    ACCESS_TOKEN_KEY,
  )

const initialRefreshToken =
  localStorage.getItem(
    REFRESH_TOKEN_KEY,
  )

const initialUser =
  readStoredUser()

export const useAuthStore =
  create<AuthState>((set) => ({
    user: initialUser,

    accessToken:
      initialAccessToken,

    refreshToken:
      initialRefreshToken,

    isAuthenticated: Boolean(
      initialAccessToken &&
        initialUser,
    ),

    isInitializing: true,

    setAuth: (
      user,
      accessToken,
      refreshToken,
    ) => {
      localStorage.setItem(
        ACCESS_TOKEN_KEY,
        accessToken,
      )

      localStorage.setItem(
        REFRESH_TOKEN_KEY,
        refreshToken,
      )

      localStorage.setItem(
        USER_KEY,
        JSON.stringify(user),
      )

      set({
        user,
        accessToken,
        refreshToken,
        isAuthenticated: true,
        isInitializing: false,
      })
    },

    setUser: (user) => {
      if (user) {
        localStorage.setItem(
          USER_KEY,
          JSON.stringify(user),
        )
      } else {
        localStorage.removeItem(
          USER_KEY,
        )
      }

      set((state) => ({
        user,
        isAuthenticated: Boolean(
          user &&
            state.accessToken,
        ),
      }))
    },

    setInitializing: (
      isInitializing,
    ) => {
      set({
        isInitializing,
      })
    },

    clearAuth: () => {
      clearStoredAuth()

      set({
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        isInitializing: false,
      })
    },

    logout: () => {
      clearStoredAuth()

      set({
        user: null,
        accessToken: null,
        refreshToken: null,
        isAuthenticated: false,
        isInitializing: false,
      })
    },
  }))