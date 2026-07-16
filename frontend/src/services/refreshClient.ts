import axios from "axios"

import type {
  TokenResponse,
} from "@/types/auth"

const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL

if (!apiBaseUrl) {
  throw new Error(
    "VITE_API_BASE_URL is not configured",
  )
}

export const refreshClient =
  axios.create({
    baseURL: apiBaseUrl,
    timeout: 15000,
    headers: {
      "Content-Type":
        "application/json",
    },
  })

export async function requestNewTokens(
  refreshToken: string,
): Promise<TokenResponse> {
  const response =
    await refreshClient.post<TokenResponse>(
      "/auth/refresh",
      {
        refresh_token: refreshToken,
      },
    )

  return response.data
}