import {
  AxiosError,
} from "axios"

interface ErrorResponse {
  detail?:
    | string
    | Array<{
        msg?: string
      }>

  message?: string
}

export function getApiError(
  error: unknown,
  fallbackMessage =
    "Something went wrong.",
): string {
  if (
    error instanceof AxiosError
  ) {
    const data =
      error.response
        ?.data as
        | ErrorResponse
        | undefined

    if (
      typeof data?.detail ===
      "string"
    ) {
      return data.detail
    }

    if (
      Array.isArray(
        data?.detail,
      )
    ) {
      const validationMessage =
        data.detail
          .map(
            (item) =>
              item.msg,
          )
          .filter(Boolean)
          .join(", ")

      if (validationMessage) {
        return validationMessage
      }
    }

    if (data?.message) {
      return data.message
    }

    if (error.message) {
      return error.message
    }
  }

  if (
    error instanceof Error
  ) {
    return error.message
  }

  return fallbackMessage
}