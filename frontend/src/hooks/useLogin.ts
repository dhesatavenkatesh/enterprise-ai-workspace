import {
  useMutation,
} from "@tanstack/react-query"

import {
  authService,
} from "@/services/authService"

import {
  queryClient,
} from "@/lib/queryClient"

import {
  queryKeys,
} from "@/services/queryKeys"

import {
  useAuthStore,
} from "@/store/authStore"

import type {
  LoginRequest,
} from "@/types/auth"

export function useLogin() {
  const setAuth =
    useAuthStore(
      (state) => state.setAuth,
    )

  return useMutation({
    mutationFn: (
      payload: LoginRequest,
    ) =>
      authService.login(payload),

    onSuccess: (
      response,
    ) => {
      setAuth(response)

      queryClient.setQueryData(
        queryKeys.auth.currentUser,
        response.user,
      )
    },
  })
}