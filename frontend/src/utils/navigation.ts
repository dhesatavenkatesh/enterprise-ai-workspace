import type {
  LucideIcon,
} from "lucide-react"

import {
  BarChart3,
  Bot,
  CheckSquare,
  Database,
  FileClock,
  KeyRound,
  LayoutDashboard,
  MessageSquare,
  Network,
  Settings,
  ShieldCheck,
  Sparkles,
  User,
  UserCog,
  Users,
  Workflow,
  Wrench,
} from "lucide-react"

import type {
  UserRole,
} from "@/types/auth"

export interface NavigationItem {
  title: string
  path: string
  icon: LucideIcon
  allowedRoles?: UserRole[]
  section?: "workspace" | "administration" | "account"
}

const managementRoles: UserRole[] = [
  "Admin",
  "Manager",
  "HR",
  "Support",
]

const adminRoles: UserRole[] = [
  "Admin",
]

export const navigationItems: NavigationItem[] = [
  /*
  |--------------------------------------------------------------------------
  | Workspace routes
  |--------------------------------------------------------------------------
  */

  {
    title: "Dashboard",
    path: "/dashboard",
    icon: LayoutDashboard,
    section: "workspace",
  },

  {
    title: "AI Chat",
    path: "/ai-chat",
    icon: MessageSquare,
    section: "workspace",
  },

  {
    title: "Prompt Templates",
    path: "/prompt-templates",
    icon: Sparkles,
    section: "workspace",
  },

  {
    title: "Knowledge Base",
    path: "/knowledge-base",
    icon: Database,
    section: "workspace",
  },

  {
    title: "Orchestrator",
    path: "/orchestrator",
    icon: Network,
    allowedRoles: managementRoles,
    section: "workspace",
  },

  {
    title: "Agents",
    path: "/agents",
    icon: Bot,
    allowedRoles: managementRoles,
    section: "workspace",
  },

  {
    title: "Workflows",
    path: "/workflows",
    icon: Workflow,
    allowedRoles: managementRoles,
    section: "workspace",
  },

  {
    title: "MCP Tools",
    path: "/mcp-tools",
    icon: Wrench,
    allowedRoles: managementRoles,
    section: "workspace",
  },

  {
    title: "Approvals",
    path: "/approvals",
    icon: CheckSquare,
    allowedRoles: managementRoles,
    section: "workspace",
  },

  {
    title: "Analytics",
    path: "/analytics",
    icon: BarChart3,
    allowedRoles: managementRoles,
    section: "workspace",
  },

  /*
  |--------------------------------------------------------------------------
  | Administration routes
  |--------------------------------------------------------------------------
  */

  {
    title: "Admin Dashboard",
    path: "/admin",
    icon: ShieldCheck,
    allowedRoles: adminRoles,
    section: "administration",
  },

  {
    title: "User Management",
    path: "/admin/users",
    icon: Users,
    allowedRoles: adminRoles,
    section: "administration",
  },

  {
    title: "Role Management",
    path: "/admin/roles",
    icon: UserCog,
    allowedRoles: adminRoles,
    section: "administration",
  },

  {
    title: "Permission Management",
    path: "/admin/permissions",
    icon: KeyRound,
    allowedRoles: adminRoles,
    section: "administration",
  },

  {
    title: "Role Permissions",
    path: "/admin/role-permissions",
    icon: ShieldCheck,
    allowedRoles: adminRoles,
    section: "administration",
  },

  {
    title: "Audit Logs",
    path: "/admin/audit-logs",
    icon: FileClock,
    allowedRoles: adminRoles,
    section: "administration",
  },

  /*
  |--------------------------------------------------------------------------
  | Account routes
  |--------------------------------------------------------------------------
  */

  {
    title: "Profile",
    path: "/profile",
    icon: User,
    section: "account",
  },

  {
    title: "Settings",
    path: "/settings",
    icon: Settings,
    allowedRoles: adminRoles,
    section: "account",
  },
]