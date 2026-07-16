import {
  BarChart3,
  Bot,
  BrainCircuit,
  Database,
  LayoutDashboard,
  Settings,
  Workflow,
} from "lucide-react"

import type {
  NavigationItem,
} from "@/types/navigation"

export const navigationItems:
  NavigationItem[] = [
    {
      title: "Dashboard",
      path: "/dashboard",
      icon: LayoutDashboard,
    },
    {
      title: "AI Chat",
      path: "/ai-chat",
      icon: BrainCircuit,
    },
    {
      title: "Knowledge Base",
      path: "/knowledge-base",
      icon: Database,
    },
    {
      title: "Agents",
      path: "/agents",
      icon: Bot,
      allowedRoles: [
        "Admin",
        "Manager",
        "HR",
        "Support",
      ],
    },
    {
      title: "Workflows",
      path: "/workflows",
      icon: Workflow,
      allowedRoles: [
        "Admin",
        "Manager",
        "HR",
        "Support",
      ],
    },
    {
      title: "Analytics",
      path: "/analytics",
      icon: BarChart3,
      allowedRoles: [
        "Admin",
        "Manager",
        "HR",
        "Support",
      ],
    },
    {
      title: "Settings",
      path: "/settings",
      icon: Settings,
      allowedRoles: [
        "Admin",
      ],
    },
  ]