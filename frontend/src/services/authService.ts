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
        "/auth/register",
        payload,
      )

    return response.data
  },

  async login(
    payload: LoginRequest,
  ): Promise<TokenResponse> {
    const response =
      await apiClient.post<TokenResponse>(
        "/auth/login",
        payload,
      )

    return response.data
  },

  async getMe():
    Promise<AuthUser> {
    const response =
      await apiClient.get<AuthUser>(
        "/auth/me",
      )

    return response.data
  },

  async refresh(
    refreshToken: string,
  ): Promise<TokenResponse> {
    const response =
      await refreshClient.post<TokenResponse>(
        "/auth/refresh",
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
        "/auth/logout",
        {
          refresh_token:
            refreshToken,
        },
      )

    return response.data
  },
}