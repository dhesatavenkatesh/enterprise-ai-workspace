import axios, {
  type AxiosError,
  type AxiosInstance,
} from "axios"

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ??
  "http://127.0.0.1:8000"

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    "Content-Type": "application/json",
  },
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token")

  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }

  return config
})

export function getApiErrorMessage(
  error: unknown,
): string {
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<{
      detail?: string
      message?: string
    }>

    const detail = axiosError.response?.data?.detail

    if (typeof detail === "string") {
      return detail
    }

    return (
      axiosError.response?.data?.message ??
      axiosError.message ??
      "Request failed"
    )
  }

  if (error instanceof Error) {
    return error.message
  }

  return "An unexpected error occurred"
}

export default api