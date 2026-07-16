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

interface SidebarProps {
  collapsed: boolean
  mobileOpen: boolean
  onCollapse: () => void
  onMobileClose: () => void
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

  const filteredNavigation =
    navigationItems.filter((item) => {
      if (!item.allowedRoles) {
        return true
      }

      if (user?.role === "Admin") {
        return true
      }

      return user
        ? item.allowedRoles.includes(
            user.role,
          )
        : false
    })

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
          "fixed inset-y-0 left-0 z-50 flex flex-col border-r border-slate-800 bg-slate-950 text-white transition-all duration-300",
          collapsed
            ? "w-20"
            : "w-64",
          mobileOpen
            ? "translate-x-0"
            : "-translate-x-full lg:translate-x-0",
        ].join(" ")}
      >
        <div className="flex h-16 items-center justify-between border-b border-slate-800 px-4">
          <div className="flex items-center gap-3 overflow-hidden">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-violet-600">
              <BrainCircuit className="h-6 w-6" />
            </div>

            {!collapsed && (
              <div className="min-w-0">
                <p className="truncate font-semibold">
                  Enterprise AI
                </p>

                <p className="truncate text-xs text-slate-400">
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
            className="text-slate-300 hover:bg-slate-800 hover:text-white lg:hidden"
          >
            <X className="h-5 w-5" />
          </Button>
        </div>

        <nav className="flex-1 space-y-1 overflow-y-auto p-3">
          {filteredNavigation.map(
            (item) => {
              const Icon = item.icon

              return (
                <NavLink
                  key={item.path}
                  to={item.path}
                  onClick={
                    onMobileClose
                  }
                  title={
                    collapsed
                      ? item.title
                      : undefined
                  }
                  className={({
                    isActive,
                  }) =>
                    [
                      "flex items-center rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                      collapsed
                        ? "justify-center"
                        : "gap-3",
                      isActive
                        ? "bg-violet-600 text-white"
                        : "text-slate-300 hover:bg-slate-800 hover:text-white",
                    ].join(" ")
                  }
                >
                  <Icon className="h-5 w-5 shrink-0" />

                  {!collapsed && (
                    <span>
                      {item.title}
                    </span>
                  )}
                </NavLink>
              )
            },
          )}
        </nav>

        <div className="hidden border-t border-slate-800 p-3 lg:block">
          <Button
            type="button"
            variant="ghost"
            onClick={onCollapse}
            className={[
              "w-full text-slate-300 hover:bg-slate-800 hover:text-white",
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