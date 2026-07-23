import {
  Navigate,
  Outlet,
} from "react-router-dom"

import {
  LoadingScreen,
} from "@/components/common/LoadingScreen"

import {
  useAuthStore,
} from "@/store/authStore"

interface RoleRouteProps {
  allowedRoles: string[]
}

export function RoleRoute({
  allowedRoles,
}: RoleRouteProps) {
  const {
    user,
    isAuthenticated,
    isInitializing,
  } = useAuthStore()

  if (isInitializing) {
    return (
      <LoadingScreen message="Checking permissions..." />
    )
  }

  if (!isAuthenticated || !user) {
    return (
      <Navigate
        to="/login"
        replace
      />
    )
  }

  const normalizedUserRole =
    user.role.trim().toLowerCase()

  const normalizedAllowedRoles =
    allowedRoles.map((role) =>
      role.trim().toLowerCase(),
    )

  const hasAccess =
    normalizedAllowedRoles.includes(
      normalizedUserRole,
    )

  if (!hasAccess) {
    return (
      <Navigate
        to="/unauthorized"
        replace
      />
    )
  }

  return <Outlet />
}