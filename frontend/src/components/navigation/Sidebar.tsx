import {
  BrainCircuit,
  ChevronLeft,
  ChevronRight,
  X,
} from "lucide-react"

import {
  NavLink,
} from "react-router-dom"

import {
  Button,
} from "@/components/ui/button"

import {
  useAuthStore,
} from "@/store/authStore"

import {
  navigationItems,
} from "@/utils/navigation"

import type {
  NavigationItem,
} from "@/utils/navigation"

interface SidebarProps {
  collapsed: boolean
  mobileOpen: boolean
  onCollapse: () => void
  onMobileClose: () => void
}

interface AuthUserWithRole {
  role?: string
  role_name?: string
  roleName?: string
  role_details?: {
    name?: string
  }
}

function getUserRole(
  user: AuthUserWithRole | null | undefined,
): string {
  const role =
    user?.role ??
    user?.role_name ??
    user?.roleName ??
    user?.role_details?.name ??
    ""

  return role.trim().toLowerCase()
}

export function Sidebar({
  collapsed,
  mobileOpen,
  onCollapse,
  onMobileClose,
}: SidebarProps) {
  const user = useAuthStore(
    (state) => state.user,
  )

  const userRole = getUserRole(
    user as AuthUserWithRole | null,
  )

  const filteredNavigation =
    navigationItems.filter((item) => {
      if (!item.allowedRoles?.length) {
        return true
      }

      if (!userRole) {
        return false
      }

      return item.allowedRoles.some(
        (allowedRole) =>
          allowedRole
            .trim()
            .toLowerCase() === userRole,
      )
    })

  const workspaceItems =
    filteredNavigation.filter(
      (item) =>
        item.section === "workspace" ||
        !item.section,
    )

  const administrationItems =
    filteredNavigation.filter(
      (item) =>
        item.section === "administration",
    )

  const accountItems =
    filteredNavigation.filter(
      (item) =>
        item.section === "account",
    )

  const renderNavigationItem = (
    item: NavigationItem,
  ) => {
    const Icon = item.icon

    return (
      <NavLink
        key={item.path}
        to={item.path}
        onClick={onMobileClose}
        title={
          collapsed
            ? item.title
            : undefined
        }
        className={({
          isActive,
        }) =>
          [
            "flex items-center rounded-xl px-3 py-2.5 text-sm font-medium transition-all duration-200",
            collapsed
              ? "justify-center"
              : "gap-3",
            isActive
              ? "bg-violet-600 text-white shadow-md shadow-violet-900/20"
              : "text-slate-700 hover:bg-violet-50 hover:text-violet-700",
          ].join(" ")
        }
      >
        <Icon className="h-5 w-5 shrink-0" />

        {!collapsed && (
          <span className="truncate">
            {item.title}
          </span>
        )}
      </NavLink>
    )
  }

  return (
    <>
      {mobileOpen && (
        <button
          type="button"
          aria-label="Close sidebar"
          onClick={onMobileClose}
          className="fixed inset-0 z-40 bg-black/50 lg:hidden"
        />
      )}

      <aside
        className={[
          "fixed inset-y-0 left-0 z-50 flex flex-col border-r border-slate-200 bg-white text-slate-900 transition-all duration-300",
          collapsed
            ? "w-20"
            : "w-64",
          mobileOpen
            ? "translate-x-0"
            : "-translate-x-full lg:translate-x-0",
        ].join(" ")}
      >
        <div className="flex h-16 shrink-0 items-center justify-between border-b border-slate-200 px-4">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-violet-600 text-white shadow-md">
              <BrainCircuit className="h-6 w-6" />
            </div>

            {!collapsed && (
              <div className="min-w-0">
                <p className="truncate font-semibold text-slate-900">
                  Enterprise AI
                </p>

                <p className="truncate text-xs text-slate-500">
                  Workspace
                </p>
              </div>
            )}
          </div>

          <Button
            type="button"
            variant="ghost"
            size="icon"
            onClick={onMobileClose}
            className="text-slate-600 hover:bg-slate-100 lg:hidden"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        <nav className="flex-1 overflow-y-auto p-3">
          {!collapsed && (
            <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
              Workspace
            </p>
          )}

          <div className="space-y-1">
            {workspaceItems.map(
              renderNavigationItem,
            )}
          </div>

          {administrationItems.length > 0 && (
            <>
              <div className="my-4 border-t border-slate-200" />

              {!collapsed && (
                <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Administration
                </p>
              )}

              <div className="space-y-1">
                {administrationItems.map(
                  renderNavigationItem,
                )}
              </div>
            </>
          )}

          {accountItems.length > 0 && (
            <>
              <div className="my-4 border-t border-slate-200" />

              {!collapsed && (
                <p className="mb-2 px-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Account
                </p>
              )}

              <div className="space-y-1">
                {accountItems.map(
                  renderNavigationItem,
                )}
              </div>
            </>
          )}
        </nav>

        <div className="hidden shrink-0 border-t border-slate-200 p-3 lg:block">
          <Button
            type="button"
            variant="ghost"
            onClick={onCollapse}
            className={[
              "w-full text-slate-600 hover:bg-slate-100 hover:text-slate-900",
              collapsed
                ? "justify-center px-0"
                : "justify-between",
            ].join(" ")}
          >
            {!collapsed && (
              <span>
                Collapse sidebar
              </span>
            )}

            {collapsed ? (
              <ChevronRight className="h-5 w-5" />
            ) : (
              <ChevronLeft className="h-5 w-5" />
            )}
          </Button>
        </div>
      </aside>
    </>
  )
}