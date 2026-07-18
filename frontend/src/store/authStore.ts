import {
  create,
} from "zustand"

import type {
  AuthUser,
  TokenResponse,
} from "@/types/auth"

import {
  tokenStorage,
} from "@/utils/tokenStorage"

interface AuthState {
  user: AuthUser | null

  isAuthenticated: boolean

  isInitializing: boolean

  setAuth: (
    response: TokenResponse,
  ) => void

  updateTokens: (
    response: TokenResponse,
  ) => void

  setUser: (
    user: AuthUser | null,
  ) => void

  setInitializing: (
    value: boolean,
  ) => void

  clearAuth: () => void
}

export const useAuthStore =
  create<AuthState>((set) => ({
    user: null,

    isAuthenticated: Boolean(
      tokenStorage.getAccessToken(),
    ),

    isInitializing: true,

    setAuth: (
      response: TokenResponse,
    ) => {
      tokenStorage.setTokens(
        response.access_token,
        response.refresh_token,
      )

      set({
        user: response.user,
        isAuthenticated: true,
        isInitializing: false,
      })
    },

    updateTokens: (
      response: TokenResponse,
    ) => {
      tokenStorage.setTokens(
        response.access_token,
        response.refresh_token,
      )

      set({
        user: response.user,
        isAuthenticated: true,
      })
    },

    setUser: (
      user: AuthUser | null,
    ) => {
      set({
        user,
        isAuthenticated:
          Boolean(user),
      })
    },

    setInitializing: (
      value: boolean,
    ) => {
      set({
        isInitializing: value,
      })
    },

    clearAuth: () => {
      tokenStorage.clearTokens()

      set({
        user: null,
        isAuthenticated: false,
        isInitializing: false,
      })
    },
  }))