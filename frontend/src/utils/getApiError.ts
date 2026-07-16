import axios from "axios"

import type {
  ApiErrorResponse,
  ValidationErrorItem,
} from "@/types/api"

function getValidationMessage(
  item: ValidationErrorItem,
): string {
  return (
    item.message ??
    item.msg ??
    "Validation failed"
  )
}

export function getApiError(
  error: unknown,
): string {
  if (
    axios.isAxiosError<
      ApiErrorResponse
    >(error)
  ) {
    const responseData =
      error.response?.data

    if (
      responseData?.message
    ) {
      return responseData.message
    }

    if (
      typeof responseData?.detail ===
      "string"
    ) {
      return responseData.detail
    }

    if (
      Array.isArray(
        responseData?.detail,
      )
    ) {
      return responseData.detail
        .map(
          getValidationMessage,
        )
        .join(", ")
    }

    if (
      responseData?.errors &&
      responseData.errors.length > 0
    ) {
      return responseData.errors
        .map(
          getValidationMessage,
        )
        .join(", ")
    }

    if (!error.response) {
      return (
        "Unable to connect to " +
        "the backend server."
      )
    }

    switch (
      error.response.status
    ) {
      case 400:
        return "Invalid request."

      case 401:
        return (
          "Authentication failed."
        )

      case 403:
        return "Permission Denied"

      case 404:
        return (
          "Requested resource " +
          "was not found."
        )

      case 409:
        return (
          "The requested record " +
          "already exists."
        )

      case 422:
        return (
          "Please check the " +
          "submitted information."
        )

      case 500:
        return (
          "The server encountered " +
          "an unexpected error."
        )

      default:
        return (
          "The request could not " +
          "be completed."
        )
    }
  }

  if (
    error instanceof Error
  ) {
    return error.message
  }

  return (
    "An unexpected error occurred."
  )
}