export type UserRole =
  | "Admin"
  | "HR"
  | "Employee"
  | "Manager"
  | "Support"

export interface AuthUser {
  id: number
  name: string
  email: string
  role: UserRole
  status: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface RegisterRequest {
  name: string
  email: string
  password: string
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
  user: AuthUser
}

export interface MessageResponse {
  message: string
}