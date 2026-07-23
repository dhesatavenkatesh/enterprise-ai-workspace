export interface AdminDeleteResponse {
  message: string
  deleted_user_id?: number
  deleted_role_id?: number
  deleted_permission_id?: number
}

export interface AdminUser {
  id: number
  name: string
  email: string
  role_id: number | null
  role_name: string | null
  is_active: boolean
  is_locked: boolean
  is_deleted: boolean
  status: string
  created_at: string
  updated_at: string | null
}

export interface AdminUserListResponse {
  items: AdminUser[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface AdminUserCreatePayload {
  name: string
  email: string
  password: string
  role_id: number | null
  is_active: boolean
}

export interface AdminUserUpdatePayload {
  name?: string
  email?: string
  role_id?: number | null
  is_active?: boolean
}

export interface AdminUserStatusPayload {
  is_active: boolean
}

export interface AdminPasswordResetPayload {
  new_password: string
  confirm_password: string
  force_logout: boolean
}

export interface AdminUserActionResponse {
  message: string
  user: AdminUser
}

export interface AdminUserQuery {
  page?: number
  page_size?: number
  search?: string
  status?: string
  role_id?: number
  is_active?: boolean
  include_deleted?: boolean
}

export interface AdminPermission {
  id: number
  permission_name: string
  module: string
  description: string | null
  created_at: string | null
}

export interface AdminPermissionListResponse {
  items: AdminPermission[]
  total: number
  page?: number
  page_size?: number
  total_pages?: number
}

export interface AdminPermissionCreatePayload {
  permission_name: string
  module: string
  description?: string | null
}

export interface AdminPermissionUpdatePayload {
  permission_name?: string
  module?: string
  description?: string | null
}

export interface AdminPermissionQuery {
  page?: number
  page_size?: number
  search?: string
  module?: string
}

export interface AdminRole {
  id: number
  name: string
  description: string | null
  permissions: AdminPermission[]
  permission_count: number
  user_count: number
  created_at: string
  updated_at: string | null
}

export interface AdminRoleListItem {
  id: number
  name: string
  description: string | null
  permission_count: number
  user_count: number
  created_at: string
  updated_at: string | null
}

export interface AdminRoleListResponse {
  items: AdminRoleListItem[]
  total: number
  page?: number
  page_size?: number
  total_pages?: number
}

export interface AdminRoleCreatePayload {
  name: string
  description?: string | null
  permission_ids: number[]
}

export interface AdminRoleUpdatePayload {
  name?: string
  description?: string | null
  permission_ids?: number[]
}

export interface AdminRolePermissionPayload {
  permission_ids: number[]
}

export interface AdminRoleQuery {
  page?: number
  page_size?: number
  search?: string
}

export interface DashboardUserStats {
  total: number
  active: number
  inactive: number
  locked: number
  deleted: number
}

export interface DashboardRoleStats {
  total_roles: number
  total_permissions: number
}

export interface DashboardAuditStats {
  total_logs: number
  logs_today: number
}

export interface DashboardRecentAuditLog {
  id: number
  user_id: number | null
  action: string
  resource: string
  resource_id: number | null
  ip_address: string | null
  created_at: string
}

export interface AdminDashboardResponse {
  users: DashboardUserStats
  roles: DashboardRoleStats
  audit: DashboardAuditStats
  recent_audit_logs: DashboardRecentAuditLog[]
  generated_at: string
}

export type AuditDetails =
  | Record<string, unknown>
  | unknown[]
  | string
  | number
  | boolean
  | null

export interface AdminAuditLog {
  id: number
  user_id: number | null
  user_name?: string | null
  user_email?: string | null
  action: string
  resource: string
  resource_id: number | null
  ip_address: string | null
  details: AuditDetails
  created_at: string
}

export interface AdminAuditLogListResponse {
  items: AdminAuditLog[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface AdminAuditLogQuery {
  page?: number
  page_size?: number
  user_id?: number
  action?: string
  resource?: string
  resource_id?: number
  ip_address?: string
  start_date?: string
  end_date?: string
}
