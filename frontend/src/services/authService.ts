import {
  apiClient,
} from "@/services/apiClient"

import {
  refreshClient,
} from "@/services/refreshClient"

import type {
  AuthUser,
  LoginRequest,
  MessageResponse,
  RegisterRequest,
  TokenResponse,
} from "@/types/auth"

export const authService = {
  async register(
    payload: RegisterRequest,
  ): Promise<AuthUser> {
    const response =
      await apiClient.post<AuthUser>(
        "/api/auth/register",
        payload,
      )

    return response.data
  },

  async login(
    payload: LoginRequest,
  ): Promise<TokenResponse> {
    const response =
      await apiClient.post<TokenResponse>(
        "/api/auth/login",
        payload,
      )

    return response.data
  },

  async getMe():
    Promise<AuthUser> {
    const response =
      await apiClient.get<AuthUser>(
        "/api/auth/me",
      )

    return response.data
  },

  async refresh(
    refreshToken: string,
  ): Promise<TokenResponse> {
    const response =
      await refreshClient.post<TokenResponse>(
        "/api/auth/refresh",
        {
          refresh_token:
            refreshToken,
        },
      )

    return response.data
  },

  async logout(
    refreshToken: string,
  ): Promise<MessageResponse> {
    const response =
      await apiClient.post<MessageResponse>(
        "/api/auth/logout",
        {
          refresh_token:
            refreshToken,
        },
      )

    return response.data
  },
}