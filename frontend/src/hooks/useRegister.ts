import {
  useMutation,
} from "@tanstack/react-query"

import {
  authService,
} from "@/services/authService"

import type {
  RegisterRequest,
} from "@/types/auth"

export function useRegister() {
  return useMutation({
    mutationFn: (
      payload: RegisterRequest,
    ) =>
      authService.register(
        payload,
      ),
  })
}