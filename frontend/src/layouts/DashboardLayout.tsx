import {
  Activity,
  BarChart3,
  Bot,
  BrainCircuit,
  ChevronDown,
  FileText,
  LayoutDashboard,
  LogOut,
  Menu,
  Moon,
  Settings,
  Sun,
  User,
  Workflow,
  X,
} from "lucide-react"

import {
  useEffect,
  useRef,
  useState,
} from "react"

import type {
  ComponentType,
} from "react"

import {
  NavLink,
  Outlet,
  useLocation,
  useNavigate,
} from "react-router-dom"

import { Button } from "@/components/ui/button"
import { useLogout } from "@/hooks/useLogout"
import { cn } from "@/lib/utils"
import { useAuthStore } from "@/store/authStore"

interface NavigationIconProps {
  className?: string
}

interface NavigationItem {
  label: string
  path: string
  icon: ComponentType<NavigationIconProps>
  end?: boolean
}

const mainNavigation: NavigationItem[] = [
  {
    label: "Dashboard",
    path: "/dashboard",
    icon: LayoutDashboard,
    end: true,
  },
  {
    label: "AI Chat",
    path: "/ai-chat",
    icon: BrainCircuit,
  },
  {
    label: "Prompt Templates",
    path: "/prompt-templates",
    icon: FileText,
  },
  {
    label: "Knowledge Base",
    path: "/knowledge-base",
    icon: Bot,
  },
  {
    label: "Agents",
    path: "/agents",
    icon: Activity,
  },
  {
    label: "Workflows",
    path: "/workflows",
    icon: Workflow,
  },
  {
    label: "Analytics",
    path: "/analytics",
    icon: BarChart3,
  },
]

const accountNavigation: NavigationItem[] = [
  {
    label: "Profile",
    path: "/profile",
    icon: User,
  },
  {
    label: "Settings",
    path: "/settings",
    icon: Settings,
  },
]

function getInitials(
  name?: string | null,
): string {
  if (!name?.trim()) {
    return "U"
  }

  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part.charAt(0))
    .join("")
    .toUpperCase()
}

function getPageTitle(
  pathname: string,
): string {
  const navigationItems = [
    ...mainNavigation,
    ...accountNavigation,
  ]

  const exactMatch =
    navigationItems.find(
      (item) =>
        item.path === pathname,
    )

  if (exactMatch) {
    return exactMatch.label
  }

  const partialMatch =
    navigationItems.find(
      (item) =>
        item.path !== "/dashboard" &&
        pathname.startsWith(
          `${item.path}/`,
        ),
    )

  return (
    partialMatch?.label ??
    "Enterprise AI"
  )
}

export function DashboardLayout() {
  const location = useLocation()
  const navigate = useNavigate()

  const profileMenuRef =
    useRef<HTMLDivElement | null>(
      null,
    )

  const user = useAuthStore(
    (state) => state.user,
  )

  const logoutMutation = useLogout()

  const [
    mobileSidebarOpen,
    setMobileSidebarOpen,
  ] = useState(false)

  const [
    profileMenuOpen,
    setProfileMenuOpen,
  ] = useState(false)

  const [darkMode, setDarkMode] =
    useState<boolean>(() => {
      if (
        typeof window ===
        "undefined"
      ) {
        return false
      }

      const savedTheme =
        window.localStorage.getItem(
          "theme",
        )

      if (savedTheme === "dark") {
        return true
      }

      if (savedTheme === "light") {
        return false
      }

      return window.matchMedia(
        "(prefers-color-scheme: dark)",
      ).matches
    })

  const pageTitle =
    getPageTitle(location.pathname)

  const userName =
    user?.name?.trim() ||
    "Enterprise User"

  const userEmail =
    user?.email ||
    "user@example.com"

  const userRole =
    String(user?.role || "User")

  useEffect(() => {
    document.documentElement.classList.toggle(
      "dark",
      darkMode,
    )

    window.localStorage.setItem(
      "theme",
      darkMode
        ? "dark"
        : "light",
    )
  }, [darkMode])

  useEffect(() => {
    setMobileSidebarOpen(false)
    setProfileMenuOpen(false)
  }, [location.pathname])

  useEffect(() => {
    const handleOutsideClick = (
      event: MouseEvent,
    ): void => {
      const clickedNode =
        event.target as Node

      if (
        profileMenuRef.current &&
        !profileMenuRef.current.contains(
          clickedNode,
        )
      ) {
        setProfileMenuOpen(false)
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

  useEffect(() => {
    const handleEscapeKey = (
      event: KeyboardEvent,
    ): void => {
      if (event.key !== "Escape") {
        return
      }

      setMobileSidebarOpen(false)
      setProfileMenuOpen(false)
    }

    window.addEventListener(
      "keydown",
      handleEscapeKey,
    )

    return () => {
      window.removeEventListener(
        "keydown",
        handleEscapeKey,
      )
    }
  }, [])

  const handleLogout =
    async (): Promise<void> => {
      try {
        await logoutMutation.mutateAsync()
      } finally {
        navigate("/login", {
          replace: true,
        })
      }
    }

  const renderNavigationItem = (
    item: NavigationItem,
  ) => {
    const Icon = item.icon

    return (
      <NavLink
        key={item.path}
        to={item.path}
        end={item.end}
        onClick={() => {
          setMobileSidebarOpen(false)
        }}
        className={({
          isActive,
        }) =>
          cn(
            "group flex h-11 items-center gap-3 rounded-xl px-3 text-sm font-medium transition-colors",
            isActive
              ? "bg-violet-600 text-white shadow-sm shadow-violet-500/20"
              : "text-muted-foreground hover:bg-muted hover:text-foreground",
          )
        }
      >
        {({ isActive }) => (
          <>
            <Icon
              className={cn(
                "h-5 w-5 shrink-0",
                isActive
                  ? "text-white"
                  : "text-muted-foreground transition-colors group-hover:text-foreground",
              )}
            />

            <span className="truncate">
              {item.label}
            </span>
          </>
        )}
      </NavLink>
    )
  }

  const sidebarContent = (
    <div className="flex h-full min-h-0 flex-col bg-card">
      <div className="flex h-16 shrink-0 items-center justify-between border-b px-4">
        <NavLink
          to="/dashboard"
          className="flex min-w-0 items-center gap-3"
          onClick={() => {
            setMobileSidebarOpen(false)
          }}
        >
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-violet-600 to-indigo-600 text-white shadow-md shadow-violet-500/20">
            <BrainCircuit className="h-6 w-6" />
          </div>

          <div className="min-w-0">
            <p className="truncate text-sm font-bold">
              Enterprise AI
            </p>

            <p className="truncate text-xs text-muted-foreground">
              Workspace
            </p>
          </div>
        </NavLink>

        <Button
          type="button"
          variant="ghost"
          size="icon"
          className="lg:hidden"
          aria-label="Close sidebar"
          onClick={() => {
            setMobileSidebarOpen(false)
          }}
        >
          <X className="h-5 w-5" />
        </Button>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto px-3 py-4">
        <div>
          <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Workspace
          </p>

          <nav className="space-y-1">
            {mainNavigation.map(
              renderNavigationItem,
            )}
          </nav>
        </div>

        <div className="my-5 border-t" />

        <div>
          <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Account
          </p>

          <nav className="space-y-1">
            {accountNavigation.map(
              renderNavigationItem,
            )}
          </nav>
        </div>
      </div>

      <div className="shrink-0 border-t p-3">
        <div className="rounded-xl bg-muted/50 p-3">
          <div className="flex min-w-0 items-center gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-violet-600 text-sm font-semibold text-white">
              {getInitials(userName)}
            </div>

            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">
                {userName}
              </p>

              <p className="truncate text-xs text-muted-foreground">
                {userEmail}
              </p>
            </div>
          </div>

          <Button
            type="button"
            variant="ghost"
            className="mt-3 h-9 w-full justify-start text-muted-foreground hover:text-destructive"
            disabled={
              logoutMutation.isPending
            }
            onClick={() => {
              void handleLogout()
            }}
          >
            <LogOut className="h-4 w-4" />

            {logoutMutation.isPending
              ? "Signing out..."
              : "Sign out"}
          </Button>
        </div>
      </div>
    </div>
  )

  return (
    <div className="min-h-screen bg-muted/20">
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-72 border-r bg-card lg:block">
        {sidebarContent}
      </aside>

      <div
        className={cn(
          "fixed inset-y-0 left-0 z-50 w-[85%] max-w-72 border-r bg-card shadow-2xl transition-transform duration-300 lg:hidden",
          mobileSidebarOpen
            ? "translate-x-0"
            : "-translate-x-full",
        )}
      >
        {sidebarContent}
      </div>

      {mobileSidebarOpen && (
        <button
          type="button"
          aria-label="Close sidebar overlay"
          onClick={() => {
            setMobileSidebarOpen(false)
          }}
          className="fixed inset-0 z-40 bg-black/50 backdrop-blur-[1px] lg:hidden"
        />
      )}

      <div className="min-h-screen lg:pl-72">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b bg-background/95 px-4 backdrop-blur supports-[backdrop-filter]:bg-background/80 sm:px-6">
          <div className="flex min-w-0 items-center gap-3">
            <Button
              type="button"
              variant="ghost"
              size="icon"
              className="lg:hidden"
              aria-label="Open sidebar"
              onClick={() => {
                setMobileSidebarOpen(true)
              }}
            >
              <Menu className="h-5 w-5" />
            </Button>

            <div className="min-w-0">
              <h1 className="truncate text-base font-semibold sm:text-lg">
                {pageTitle}
              </h1>

              <p className="hidden truncate text-xs text-muted-foreground sm:block">
                Manage your enterprise AI
                workspace
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <Button
              type="button"
              variant="ghost"
              size="icon"
              aria-label={
                darkMode
                  ? "Enable light mode"
                  : "Enable dark mode"
              }
              title={
                darkMode
                  ? "Light mode"
                  : "Dark mode"
              }
              onClick={() => {
                setDarkMode(
                  (currentTheme) =>
                    !currentTheme,
                )
              }}
            >
              {darkMode ? (
                <Sun className="h-5 w-5" />
              ) : (
                <Moon className="h-5 w-5" />
              )}
            </Button>

            <div
              ref={profileMenuRef}
              className="relative"
            >
              <button
                type="button"
                aria-expanded={
                  profileMenuOpen
                }
                aria-haspopup="menu"
                onClick={() => {
                  setProfileMenuOpen(
                    (currentState) =>
                      !currentState,
                  )
                }}
                className="flex items-center gap-2 rounded-xl border bg-card px-2 py-1.5 text-left transition hover:bg-muted sm:px-3"
              >
                <div className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-violet-600 text-xs font-semibold text-white">
                  {getInitials(userName)}
                </div>

                <div className="hidden min-w-0 sm:block">
                  <p className="max-w-36 truncate text-sm font-medium">
                    {userName}
                  </p>

                  <p className="max-w-36 truncate text-xs capitalize text-muted-foreground">
                    {userRole}
                  </p>
                </div>

                <ChevronDown
                  className={cn(
                    "hidden h-4 w-4 text-muted-foreground transition-transform sm:block",
                    profileMenuOpen &&
                      "rotate-180",
                  )}
                />
              </button>

              {profileMenuOpen && (
                <div
                  role="menu"
                  className="absolute right-0 mt-2 w-64 overflow-hidden rounded-xl border bg-popover shadow-xl"
                >
                  <div className="border-b px-4 py-3">
                    <p className="truncate text-sm font-medium">
                      {userName}
                    </p>

                    <p className="mt-0.5 truncate text-xs text-muted-foreground">
                      {userEmail}
                    </p>
                  </div>

                  <div className="p-1.5">
                    <button
                      type="button"
                      role="menuitem"
                      onClick={() => {
                        navigate("/profile")
                        setProfileMenuOpen(
                          false,
                        )
                      }}
                      className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm transition hover:bg-muted"
                    >
                      <User className="h-4 w-4" />
                      Profile
                    </button>

                    <button
                      type="button"
                      role="menuitem"
                      onClick={() => {
                        navigate("/settings")
                        setProfileMenuOpen(
                          false,
                        )
                      }}
                      className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm transition hover:bg-muted"
                    >
                      <Settings className="h-4 w-4" />
                      Settings
                    </button>
                  </div>

                  <div className="border-t p-1.5">
                    <button
                      type="button"
                      role="menuitem"
                      disabled={
                        logoutMutation.isPending
                      }
                      onClick={() => {
                        setProfileMenuOpen(
                          false,
                        )

                        void handleLogout()
                      }}
                      className="flex w-full items-center gap-3 rounded-lg px-3 py-2 text-sm text-destructive transition hover:bg-destructive/10 disabled:cursor-not-allowed disabled:opacity-60"
                    >
                      <LogOut className="h-4 w-4" />

                      {logoutMutation.isPending
                        ? "Signing out..."
                        : "Sign out"}
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </header>

        <main className="min-h-[calc(100vh-4rem)] p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  )
}

export default DashboardLayout