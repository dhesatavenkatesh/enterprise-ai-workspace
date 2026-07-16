import {
  useQuery,
} from "@tanstack/react-query"

import {
  authService,
} from "@/services/authService"

import {
  queryKeys,
} from "@/services/queryKeys"

import {
  useAuthStore,
} from "@/store/authStore"

import {
  tokenStorage,
} from "@/utils/tokenStorage"

export function useCurrentUser() {
  const setUser =
    useAuthStore(
      (state) => state.setUser,
    )

  return useQuery({
    queryKey:
      queryKeys.auth.currentUser,

    queryFn: async () => {
      const user =
        await authService.getMe()

      setUser(user)

      return user
    },

    enabled: Boolean(
      tokenStorage.getAccessToken() ||
      tokenStorage.getRefreshToken(),
    ),

    staleTime: 60_000,
  })
}