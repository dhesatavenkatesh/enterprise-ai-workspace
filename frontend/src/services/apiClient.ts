import axios, {
  type AxiosError,
  type InternalAxiosRequestConfig,
} from "axios"

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  "http://127.0.0.1:8000"

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    "Content-Type": "application/json",
  },
})

apiClient.interceptors.request.use(
  (
    config: InternalAxiosRequestConfig,
  ) => {
    const accessToken =
      localStorage.getItem(
        "access_token",
      )

    if (accessToken) {
      config.headers.Authorization =
        `Bearer ${accessToken}`
    }

    return config
  },
  (error: AxiosError) =>
    Promise.reject(error),
)

apiClient.interceptors.response.use(
  (response) => response,

  (error: AxiosError) => {
    const status =
      error.response?.status

    const requestUrl =
      error.config?.url ?? ""

    const isAuthRequest =
      requestUrl.includes(
        "/api/auth/login",
      ) ||
      requestUrl.includes(
        "/api/auth/register",
      ) ||
      requestUrl.includes(
        "/api/auth/refresh",
      )

    if (
      status === 401 &&
      !isAuthRequest
    ) {
      console.error(
        "Unauthorized request:",
        requestUrl,
      )
    }

    return Promise.reject(error)
  },
)