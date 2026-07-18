import {
  useMutation,
} from "@tanstack/react-query"

import {
  useNavigate,
} from "react-router-dom"

import {
  toast,
} from "sonner"

import {
  queryClient,
} from "@/lib/queryClient"

import {
  authService,
} from "@/services/authService"

import {
  useAuthStore,
} from "@/store/authStore"

import {
  tokenStorage,
} from "@/utils/tokenStorage"

export function useLogout() {
  const navigate = useNavigate()

  const clearAuth =
    useAuthStore(
      (state) => state.clearAuth,
    )

  return useMutation({
    mutationFn: async () => {
      const refreshToken =
        tokenStorage.getRefreshToken()

      if (!refreshToken) {
        return
      }

      await authService.logout(
        refreshToken,
      )
    },

    onSettled: () => {
      clearAuth()
      queryClient.clear()

      toast.success(
        "Logged out successfully",
      )

      navigate("/login", {
        replace: true,
      })
    },
  })
}