import {
  useState,
} from "react"

import {
  Outlet,
} from "react-router-dom"

import {
  Footer,
} from "@/components/common/Footer"

import {
  Header,
} from "@/components/navigation/Header"

import {
  Sidebar,
} from "@/components/navigation/Sidebar"

export function DashboardLayout() {
  const [collapsed, setCollapsed] =
    useState(false)

  const [mobileOpen, setMobileOpen] =
    useState(false)

  return (
    <div className="min-h-screen bg-slate-100">
      <Sidebar
        collapsed={collapsed}
        mobileOpen={mobileOpen}
        onCollapse={() =>
          setCollapsed(
            (current) => !current,
          )
        }
        onMobileClose={() =>
          setMobileOpen(false)
        }
      />

      <div
        className={[
          "flex min-h-screen flex-col transition-all duration-300",
          collapsed
            ? "lg:ml-20"
            : "lg:ml-64",
        ].join(" ")}
      >
        <Header
          onMenuClick={() =>
            setMobileOpen(true)
          }
        />

        <main className="flex-1 p-4 md:p-6">
          <Outlet />
        </main>

        <Footer />
      </div>
    </div>
  )
}