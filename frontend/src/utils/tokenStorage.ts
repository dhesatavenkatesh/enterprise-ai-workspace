const ACCESS_TOKEN_KEY =
  "enterprise_ai_access_token"

const REFRESH_TOKEN_KEY =
  "enterprise_ai_refresh_token"

export interface StoredTokens {
  accessToken: string
  refreshToken: string
}

export const tokenStorage = {
  getAccessToken(): string | null {
    return localStorage.getItem(
      ACCESS_TOKEN_KEY,
    )
  },

  getRefreshToken(): string | null {
    return localStorage.getItem(
      REFRESH_TOKEN_KEY,
    )
  },

  getTokens(): StoredTokens | null {
    const accessToken =
      this.getAccessToken()

    const refreshToken =
      this.getRefreshToken()

    if (
      !accessToken ||
      !refreshToken
    ) {
      return null
    }

    return {
      accessToken,
      refreshToken,
    }
  },

  setAccessToken(
    accessToken: string,
  ): void {
    localStorage.setItem(
      ACCESS_TOKEN_KEY,
      accessToken,
    )
  },

  setRefreshToken(
    refreshToken: string,
  ): void {
    localStorage.setItem(
      REFRESH_TOKEN_KEY,
      refreshToken,
    )
  },

  setTokens(
    accessToken: string,
    refreshToken: string,
  ): void {
    this.setAccessToken(accessToken)
    this.setRefreshToken(refreshToken)
  },

  clearTokens(): void {
    localStorage.removeItem(
      ACCESS_TOKEN_KEY,
    )

    localStorage.removeItem(
      REFRESH_TOKEN_KEY,
    )
  },
}