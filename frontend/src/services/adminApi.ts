import api from "@/services/api"

import type {
  AdminAuditLogListResponse,
  AdminAuditLogQuery,
  AdminDashboardResponse,
  AdminDeleteResponse,
  AdminPasswordResetPayload,
  AdminPermission,
  AdminPermissionCreatePayload,
  AdminPermissionListResponse,
  AdminPermissionQuery,
  AdminPermissionUpdatePayload,
  AdminRole,
  AdminRoleCreatePayload,
  AdminRoleListResponse,
  AdminRolePermissionPayload,
  AdminRoleQuery,
  AdminRoleUpdatePayload,
  AdminUser,
  AdminUserActionResponse,
  AdminUserCreatePayload,
  AdminUserListResponse,
  AdminUserQuery,
  AdminUserStatusPayload,
  AdminUserUpdatePayload,
} from "@/types/admin"

/*
|--------------------------------------------------------------------------
| API paths
|--------------------------------------------------------------------------
|
| This configuration assumes src/services/api.ts uses:
|
| baseURL: "http://127.0.0.1:8000"
|
| Therefore, the paths below include "/api".
|
| When your baseURL already ends with "/api", change:
|
| const ADMIN_BASE_URL = "/api/admin"
|
| to:
|
| const ADMIN_BASE_URL = "/admin"
|
*/

const ADMIN_BASE_URL = "/api/admin"

const DASHBOARD_URL = `${ADMIN_BASE_URL}/dashboard`
const USERS_URL = `${ADMIN_BASE_URL}/users`
const ROLES_URL = `${ADMIN_BASE_URL}/roles`
const PERMISSIONS_URL = `${ADMIN_BASE_URL}/permissions`
const AUDIT_LOGS_URL = `${ADMIN_BASE_URL}/audit-logs`

/*
|--------------------------------------------------------------------------
| Admin dashboard
|--------------------------------------------------------------------------
*/

export const adminDashboardApi = {
  async getDashboard(): Promise<AdminDashboardResponse> {
    const response =
      await api.get<AdminDashboardResponse>(
        DASHBOARD_URL,
      )

    return response.data
  },
}

/*
|--------------------------------------------------------------------------
| User management
|--------------------------------------------------------------------------
*/

export const adminUsersApi = {
  async getUsers(
    query: AdminUserQuery = {},
  ): Promise<AdminUserListResponse> {
    const response =
      await api.get<AdminUserListResponse>(
        USERS_URL,
        {
          params: {
            page: query.page,
            page_size: query.page_size,
            search: query.search,
            status: query.status,
            role_id: query.role_id,
            is_active: query.is_active,
            include_deleted:
              query.include_deleted,
          },
        },
      )

    return response.data
  },

  async getUser(
    userId: number,
  ): Promise<AdminUser> {
    const response = await api.get<AdminUser>(
      `${USERS_URL}/${userId}`,
    )

    return response.data
  },

  async createUser(
    payload: AdminUserCreatePayload,
  ): Promise<AdminUser> {
    const response = await api.post<AdminUser>(
      USERS_URL,
      payload,
    )

    return response.data
  },

  async updateUser(
    userId: number,
    payload: AdminUserUpdatePayload,
  ): Promise<AdminUser> {
    const response = await api.put<AdminUser>(
      `${USERS_URL}/${userId}`,
      payload,
    )

    return response.data
  },

  async updateUserStatus(
    userId: number,
    payload: AdminUserStatusPayload,
  ): Promise<AdminUserActionResponse> {
    const response =
      await api.patch<AdminUserActionResponse>(
        `${USERS_URL}/${userId}/status`,
        payload,
      )

    return response.data
  },

  async activateUser(
    userId: number,
  ): Promise<AdminUserActionResponse> {
    return this.updateUserStatus(userId, {
      is_active: true,
    })
  },

  async deactivateUser(
    userId: number,
  ): Promise<AdminUserActionResponse> {
    return this.updateUserStatus(userId, {
      is_active: false,
    })
  },

  async resetPassword(
    userId: number,
    payload: AdminPasswordResetPayload,
  ): Promise<AdminUserActionResponse> {
    const response =
      await api.post<AdminUserActionResponse>(
        `${USERS_URL}/${userId}/reset-password`,
        payload,
      )

    return response.data
  },

  async deleteUser(
    userId: number,
  ): Promise<AdminDeleteResponse> {
    const response =
      await api.delete<AdminDeleteResponse>(
        `${USERS_URL}/${userId}`,
      )

    return response.data
  },
}

/*
|--------------------------------------------------------------------------
| Role management
|--------------------------------------------------------------------------
*/

export const adminRolesApi = {
  async getRoles(
    query: AdminRoleQuery = {},
  ): Promise<AdminRoleListResponse> {
    const response =
      await api.get<AdminRoleListResponse>(
        ROLES_URL,
        {
          params: {
            page: query.page,
            page_size: query.page_size,
            search: query.search,
          },
        },
      )

    return response.data
  },

  async getRole(
    roleId: number,
  ): Promise<AdminRole> {
    const response = await api.get<AdminRole>(
      `${ROLES_URL}/${roleId}`,
    )

    return response.data
  },

  async createRole(
    payload: AdminRoleCreatePayload,
  ): Promise<AdminRole> {
    const response = await api.post<AdminRole>(
      ROLES_URL,
      payload,
    )

    return response.data
  },

  async updateRole(
    roleId: number,
    payload: AdminRoleUpdatePayload,
  ): Promise<AdminRole> {
    const response = await api.put<AdminRole>(
      `${ROLES_URL}/${roleId}`,
      payload,
    )

    return response.data
  },

  async deleteRole(
    roleId: number,
  ): Promise<AdminDeleteResponse> {
    const response =
      await api.delete<AdminDeleteResponse>(
        `${ROLES_URL}/${roleId}`,
      )

    return response.data
  },

  /*
  |--------------------------------------------------------------------------
  | Role permissions
  |--------------------------------------------------------------------------
  */

  async getPermissions(
    query: AdminPermissionQuery = {
      page: 1,
      page_size: 500,
    },
  ): Promise<AdminPermissionListResponse> {
    const response =
      await api.get<AdminPermissionListResponse>(
        PERMISSIONS_URL,
        {
          params: {
            page: query.page,
            page_size: query.page_size,
            search: query.search,
            module: query.module,
          },
        },
      )

    return response.data
  },

  async getRolePermissions(
    roleId: number,
  ): Promise<AdminRole> {
    const response = await api.get<AdminRole>(
      `${ROLES_URL}/${roleId}`,
    )

    return response.data
  },

  async updatePermissions(
    roleId: number,
    payload: AdminRolePermissionPayload,
  ): Promise<AdminRole> {
    const response = await api.put<AdminRole>(
      `${ROLES_URL}/${roleId}/permissions`,
      payload,
    )

    return response.data
  },

  async updateRolePermissions(
    roleId: number,
    payload: AdminRolePermissionPayload,
  ): Promise<AdminRole> {
    return this.updatePermissions(
      roleId,
      payload,
    )
  },
}

/*
|--------------------------------------------------------------------------
| Permission management
|--------------------------------------------------------------------------
*/

export const adminPermissionsApi = {
  async getPermissions(
    query: AdminPermissionQuery = {},
  ): Promise<AdminPermissionListResponse> {
    const response =
      await api.get<AdminPermissionListResponse>(
        PERMISSIONS_URL,
        {
          params: {
            page: query.page,
            page_size: query.page_size,
            search: query.search,
            module: query.module,
          },
        },
      )

    return response.data
  },

  async getPermission(
    permissionId: number,
  ): Promise<AdminPermission> {
    const response =
      await api.get<AdminPermission>(
        `${PERMISSIONS_URL}/${permissionId}`,
      )

    return response.data
  },

  async createPermission(
    payload: AdminPermissionCreatePayload,
  ): Promise<AdminPermission> {
    const response =
      await api.post<AdminPermission>(
        PERMISSIONS_URL,
        payload,
      )

    return response.data
  },

  async updatePermission(
    permissionId: number,
    payload: AdminPermissionUpdatePayload,
  ): Promise<AdminPermission> {
    const response =
      await api.put<AdminPermission>(
        `${PERMISSIONS_URL}/${permissionId}`,
        payload,
      )

    return response.data
  },

  async deletePermission(
    permissionId: number,
  ): Promise<AdminDeleteResponse> {
    const response =
      await api.delete<AdminDeleteResponse>(
        `${PERMISSIONS_URL}/${permissionId}`,
      )

    return response.data
  },
}

/*
|--------------------------------------------------------------------------
| Audit logs
|--------------------------------------------------------------------------
*/

export const adminAuditApi = {
  async getAuditLogs(
    query: AdminAuditLogQuery = {},
  ): Promise<AdminAuditLogListResponse> {
    const response =
      await api.get<AdminAuditLogListResponse>(
        AUDIT_LOGS_URL,
        {
          params: {
            page: query.page,
            page_size: query.page_size,
            user_id: query.user_id,
            action: query.action,
            resource: query.resource,
            resource_id: query.resource_id,
            ip_address: query.ip_address,
            start_date: query.start_date,
            end_date: query.end_date,
          },
        },
      )

    return response.data
  },
}

/*
|--------------------------------------------------------------------------
| Compatibility aliases
|--------------------------------------------------------------------------
|
| These aliases support page files that use older API object names.
|
*/

export const adminAuditLogsApi =
  adminAuditApi