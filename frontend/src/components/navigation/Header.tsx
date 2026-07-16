import {
  Bell,
  LoaderCircle,
  LogOut,
  Menu,
  User,
} from "lucide-react"
import {
  useEffect,
  useRef,
  useState,
} from "react"
import {
  Link,
  useLocation,
} from "react-router-dom"

import { Button } from "@/components/ui/button"
import { useLogout } from "@/hooks/useLogout"
import { useAuthStore } from "@/store/authStore"

interface HeaderProps {
  onMenuClick: () => void
}

interface NotificationItemProps {
  title: string
  message: string
}

const pageTitles: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/ai-chat": "AI Chat",
  "/knowledge-base": "Knowledge Base",
  "/agents": "Agents",
  "/workflows": "Workflows",
  "/analytics": "Analytics",
  "/settings": "Settings",
  "/profile": "Profile",
}

function getPageTitle(
  pathname: string,
): string {
  return (
    pageTitles[pathname] ??
    "Enterprise AI Workspace"
  )
}

function NotificationItem({
  title,
  message,
}: NotificationItemProps) {
  return (
    <div className="rounded-lg bg-slate-50 p-3">
      <p className="text-sm font-medium text-slate-900">
        {title}
      </p>

      <p className="mt-1 text-xs leading-5 text-slate-500">
        {message}
      </p>
    </div>
  )
}

export function Header({
  onMenuClick,
}: HeaderProps) {
  const location = useLocation()

  const menuContainerRef =
    useRef<HTMLDivElement>(null)

  const [
    profileOpen,
    setProfileOpen,
  ] = useState(false)

  const [
    notificationsOpen,
    setNotificationsOpen,
  ] = useState(false)

  const user = useAuthStore(
    (state) => state.user,
  )

  const logoutMutation = useLogout()

  useEffect(() => {
    const handleOutsideClick = (
      event: MouseEvent,
    ): void => {
      const target =
        event.target as Node

      if (
        menuContainerRef.current &&
        !menuContainerRef.current.contains(
          target,
        )
      ) {
        setProfileOpen(false)
        setNotificationsOpen(false)
      }
    }

    document.addEventListener(
      "mousedown",
      handleOutsideClick,
    )

    return () => {
      document.removeEventListener(
        "mousedown",
        handleOutsideClick,
      )
    }
  }, [])

  const handleLogout = (): void => {
    logoutMutation.mutate()
  }

  const handleProfileToggle = (): void => {
    setProfileOpen(
      (current) => !current,
    )

    setNotificationsOpen(false)
  }

  const handleNotificationsToggle =
    (): void => {
      setNotificationsOpen(
        (current) => !current,
      )

      setProfileOpen(false)
    }

  const handleProfileLinkClick =
    (): void => {
      setProfileOpen(false)
      setNotificationsOpen(false)
    }

  const userInitial =
    user?.name
      .trim()
      .charAt(0)
      .toUpperCase() || "U"

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-slate-200 bg-white px-4 shadow-sm md:px-6">
      <div className="flex min-w-0 items-center gap-3">
        <Button
          type="button"
          variant="ghost"
          size="icon"
          onClick={onMenuClick}
          aria-label="Open navigation"
          className="shrink-0 lg:hidden"
        >
          <Menu className="h-5 w-5" />
        </Button>

        <div className="min-w-0">
          <h1 className="truncate text-lg font-semibold text-slate-900 md:text-xl">
            {getPageTitle(
              location.pathname,
            )}
          </h1>

          <p className="hidden truncate text-xs text-slate-500 sm:block">
            Welcome back,{" "}
            {user?.name ?? "User"}
          </p>
        </div>
      </div>

      <div
        ref={menuContainerRef}
        className="relative flex items-center gap-2"
      >
        <div className="relative">
          <Button
            type="button"
            variant="ghost"
            size="icon"
            onClick={
              handleNotificationsToggle
            }
            aria-label="Open notifications"
            aria-expanded={
              notificationsOpen
            }
            className="relative"
          >
            <Bell className="h-5 w-5" />

            <span className="absolute right-2 top-2 h-2 w-2 rounded-full bg-red-500" />
          </Button>

          {notificationsOpen && (
            <div className="absolute right-0 top-12 z-50 w-[calc(100vw-2rem)] max-w-80 rounded-xl border border-slate-200 bg-white p-4 shadow-xl">
              <div className="mb-3 flex items-center justify-between gap-3">
                <p className="font-semibold text-slate-900">
                  Notifications
                </p>

                <span className="rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-600">
                  3 new
                </span>
              </div>

              <div className="space-y-3">
                <NotificationItem
                  title="Workspace ready"
                  message="Your Enterprise AI Workspace is active."
                />

                <NotificationItem
                  title="AI features"
                  message="AI Chat and Knowledge Base modules are ready for integration."
                />

                <NotificationItem
                  title="Profile reminder"
                  message="Review and complete your employee profile."
                />
              </div>
            </div>
          )}
        </div>

        <button
          type="button"
          onClick={handleProfileToggle}
          aria-label="Open profile menu"
          aria-expanded={profileOpen}
          className="flex min-w-0 items-center gap-3 rounded-lg p-1.5 text-left transition-colors hover:bg-slate-100"
        >
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-violet-600 font-semibold text-white">
            {userInitial}
          </div>

          <div className="hidden min-w-0 max-w-40 md:block">
            <p className="truncate text-sm font-semibold text-slate-900">
              {user?.name ?? "User"}
            </p>

            <p className="truncate text-xs text-slate-500">
              {user?.role ?? "Employee"}
            </p>
          </div>
        </button>

        {profileOpen && (
          <div className="absolute right-0 top-12 z-50 w-64 rounded-xl border border-slate-200 bg-white p-2 shadow-xl">
            <div className="border-b border-slate-200 px-3 py-3">
              <p className="truncate font-semibold text-slate-900">
                {user?.name ?? "User"}
              </p>

              <p className="truncate text-sm text-slate-500">
                {user?.email ?? ""}
              </p>

              <span className="mt-2 inline-flex rounded-full bg-violet-100 px-2 py-1 text-xs font-medium text-violet-700">
                {user?.role ?? "Employee"}
              </span>
            </div>

            <Link
              to="/profile"
              onClick={
                handleProfileLinkClick
              }
              className="mt-2 flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-slate-700 transition-colors hover:bg-slate-100"
            >
              <User className="h-4 w-4" />
              View profile
            </Link>

            <button
              type="button"
              onClick={handleLogout}
              disabled={
                logoutMutation.isPending
              }
              className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-red-600 transition-colors hover:bg-red-50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {logoutMutation.isPending ? (
                <LoaderCircle className="h-4 w-4 animate-spin" />
              ) : (
                <LogOut className="h-4 w-4" />
              )}

              {logoutMutation.isPending
                ? "Logging out..."
                : "Logout"}
            </button>
          </div>
        )}
      </div>
    </header>
  )
}