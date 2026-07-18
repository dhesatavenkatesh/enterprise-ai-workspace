import axios from "axios"

import type {
  AxiosError,
  AxiosRequestConfig,
} from "axios"

import {
  emitForbidden,
  emitUnauthorized,
} from "@/utils/authEvents"

import {
  requestNewTokens,
} from "@/services/refreshClient"

import {
  tokenStorage,
} from "@/utils/tokenStorage"

const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL

if (!apiBaseUrl) {
  throw new Error(
    "VITE_API_BASE_URL is not configured",
  )
}

interface RetryableRequestConfig
  extends AxiosRequestConfig {
  _retry?: boolean
}

interface PendingRequest {
  resolve: (
    accessToken: string,
  ) => void

  reject: (
    error: unknown,
  ) => void
}

export const apiClient =
  axios.create({
    baseURL: apiBaseUrl,
    timeout: 15000,
    headers: {
      "Content-Type":
        "application/json",
    },
  })

let isRefreshing = false

let pendingRequests:
  PendingRequest[] = []

function processPendingRequests(
  error: unknown,
  accessToken: string | null,
): void {
  pendingRequests.forEach(
    ({ resolve, reject }) => {
      if (
        error ||
        !accessToken
      ) {
        reject(
          error ??
            new Error(
              "Token refresh failed",
            ),
        )

        return
      }

      resolve(accessToken)
    },
  )

  pendingRequests = []
}

apiClient.interceptors.request.use(
  (config) => {
    const accessToken =
      tokenStorage.getAccessToken()

    if (accessToken) {
      config.headers.Authorization =
        `Bearer ${accessToken}`
    }

    return config
  },

  (error: unknown) =>
    Promise.reject(error),
)

apiClient.interceptors.response.use(
  (response) => response,

  async (
    error: AxiosError,
  ): Promise<unknown> => {
    const originalRequest =
      error.config as
        | RetryableRequestConfig
        | undefined

    const status =
      error.response?.status

    if (status === 403) {
      emitForbidden()

      return Promise.reject(error)
    }

    if (
      status !== 401 ||
      !originalRequest
    ) {
      return Promise.reject(error)
    }

    const requestUrl =
      originalRequest.url ?? ""

    const isAuthenticationRequest =
      requestUrl.includes(
        "/auth/login",
      ) ||
      requestUrl.includes(
        "/auth/register",
      ) ||
      requestUrl.includes(
        "/auth/refresh",
      )

    if (isAuthenticationRequest) {
      return Promise.reject(error)
    }

    if (originalRequest._retry) {
      emitUnauthorized()

      return Promise.reject(error)
    }

    const refreshToken =
      tokenStorage.getRefreshToken()

    if (!refreshToken) {
      tokenStorage.clearTokens()
      emitUnauthorized()

      return Promise.reject(error)
    }

    if (isRefreshing) {
      try {
        const accessToken =
          await new Promise<string>(
            (resolve, reject) => {
              pendingRequests.push({
                resolve,
                reject,
              })
            },
          )

        originalRequest.headers = {
          ...originalRequest.headers,
          Authorization:
            `Bearer ${accessToken}`,
        }

        return apiClient(
          originalRequest,
        )
      } catch (
        refreshError
      ) {
        return Promise.reject(
          refreshError,
        )
      }
    }

    originalRequest._retry = true
    isRefreshing = true

    try {
      const tokenResponse =
        await requestNewTokens(
          refreshToken,
        )

      tokenStorage.setTokens(
        tokenResponse.access_token,
        tokenResponse.refresh_token,
      )

      processPendingRequests(
        null,
        tokenResponse.access_token,
      )

      originalRequest.headers = {
        ...originalRequest.headers,
        Authorization:
          `Bearer ${tokenResponse.access_token}`,
      }

      return apiClient(
        originalRequest,
      )
    } catch (
      refreshError
    ) {
      processPendingRequests(
        refreshError,
        null,
      )

      tokenStorage.clearTokens()
      emitUnauthorized()

      return Promise.reject(
        refreshError,
      )
    } finally {
      isRefreshing = false
    }
  },
)