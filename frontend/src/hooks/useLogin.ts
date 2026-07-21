import {
  useMutation,
} from "@tanstack/react-query"

import {
  authService,
} from "@/services/authService"

import {
  useAuthStore,
} from "@/store/authStore"

import type {
  LoginRequest,
  TokenResponse,
} from "@/types/auth"

export function useLogin() {
  const setAuth =
    useAuthStore(
      (state) => state.setAuth,
    )

  return useMutation<
    TokenResponse,
    Error,
    LoginRequest
  >({
    mutationFn: (
      credentials,
    ) =>
      authService.login(
        credentials,
      ),

    onSuccess: (response) => {
      setAuth(
        response.user,
        response.access_token,
        response.refresh_token,
      )
    },
  })
}