import type { LucideIcon } from "lucide-react"

import {
  BarChart3,
  Bot,
  CheckSquare,
  Database,
  LayoutDashboard,
  MessageSquare,
  Network,
  Settings,
  Sparkles,
  User,
  Workflow,
  Wrench,
} from "lucide-react"

export interface NavigationItem {
  title: string
  path: string
  icon: LucideIcon
  allowedRoles?: string[]
}

const managementRoles = [
  "Admin",
  "Manager",
  "HR",
  "Support",
]

export const navigationItems: NavigationItem[] = [
  {
    title: "Dashboard",
    path: "/dashboard",
    icon: LayoutDashboard,
  },
  {
    title: "AI Chat",
    path: "/ai-chat",
    icon: MessageSquare,
  },
  {
    title: "Prompt Templates",
    path: "/prompt-templates",
    icon: Sparkles,
  },
  {
    title: "Knowledge Base",
    path: "/knowledge-base",
    icon: Database,
  },
  {
    title: "Orchestrator",
    path: "/orchestrator",
    icon: Network,
    allowedRoles: managementRoles,
  },
  {
    title: "Agents",
    path: "/agents",
    icon: Bot,
    allowedRoles: managementRoles,
  },
  {
    title: "Workflows",
    path: "/workflows",
    icon: Workflow,
    allowedRoles: managementRoles,
  },
  {
    title: "MCP Tools",
    path: "/mcp-tools",
    icon: Wrench,
    allowedRoles: managementRoles,
  },
  {
    title: "Approvals",
    path: "/approvals",
    icon: CheckSquare,
    allowedRoles: managementRoles,
  },
  {
    title: "Analytics",
    path: "/analytics",
    icon: BarChart3,
    allowedRoles: managementRoles,
  },
  {
    title: "Profile",
    path: "/profile",
    icon: User,
  },
  {
    title: "Settings",
    path: "/settings",
    icon: Settings,
    allowedRoles: ["Admin"],
  },
]