type AuthEventHandler = () => void

let unauthorizedHandler:
  AuthEventHandler | null = null

let forbiddenHandler:
  AuthEventHandler | null = null

export function registerUnauthorizedHandler(
  handler: AuthEventHandler,
): () => void {
  unauthorizedHandler = handler

  return () => {
    if (
      unauthorizedHandler === handler
    ) {
      unauthorizedHandler = null
    }
  }
}

export function registerForbiddenHandler(
  handler: AuthEventHandler,
): () => void {
  forbiddenHandler = handler

  return () => {
    if (
      forbiddenHandler === handler
    ) {
      forbiddenHandler = null
    }
  }
}

export function emitUnauthorized(): void {
  unauthorizedHandler?.()
}

export function emitForbidden(): void {
  forbiddenHandler?.()
}