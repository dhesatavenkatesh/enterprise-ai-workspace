import {
  Navigate,
  Outlet,
} from "react-router-dom"

import {
  useAuthStore,
} from "@/store/authStore"

import type {
  UserRole,
} from "@/types/auth"

interface RoleRouteProps {
  allowedRoles: UserRole[]
}

export function RoleRoute({
  allowedRoles,
}: RoleRouteProps) {
  const {
    user,
  } = useAuthStore()

  if (!user) {
    return (
      <Navigate
        to="/login"
        replace
      />
    )
  }

  if (
    user.role !== "Admin" &&
    !allowedRoles.includes(user.role)
  ) {
    return (
      <Navigate
        to="/unauthorized"
        replace
      />
    )
  }

  return <Outlet />
}