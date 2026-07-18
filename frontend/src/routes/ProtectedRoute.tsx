import {
  Navigate,
  Outlet,
  useLocation,
} from "react-router-dom"

import {
  LoadingScreen,
} from "@/components/common/LoadingScreen"

import {
  useAuthStore,
} from "@/store/authStore"

export function ProtectedRoute() {
  const location = useLocation()

  const {
    isAuthenticated,
    isInitializing,
  } = useAuthStore()

  if (isInitializing) {
    return (
      <LoadingScreen message="Checking authentication..." />
    )
  }

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
        state={{
          from: location,
        }}
      />
    )
  }

  return <Outlet />
}