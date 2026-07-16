import type {
  LucideIcon,
} from "lucide-react"

import type {
  UserRole,
} from "@/types/auth"

export interface NavigationItem {
  title: string
  path: string
  icon: LucideIcon
  allowedRoles?: UserRole[]
}