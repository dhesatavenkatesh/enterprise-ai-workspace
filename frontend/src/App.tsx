import {
  Navigate,
  Route,
  Routes,
} from "react-router-dom"

import {
  AuthLayout,
} from "@/layouts/AuthLayout"

import {
  DashboardLayout,
} from "@/layouts/DashboardLayout"

import {
  NotFoundPage,
} from "@/pages/NotFoundPage"

import {
  ForgotPasswordPage,
} from "@/pages/auth/ForgotPasswordPage"

import {
  LoginPage,
} from "@/pages/auth/LoginPage"

import {
  RegisterPage,
} from "@/pages/auth/RegisterPage"

import {
  ResetPasswordPage,
} from "@/pages/auth/ResetPasswordPage"

import {
  UnauthorizedPage,
} from "@/pages/auth/UnauthorizedPage"

import {
  AgentsPage,
} from "@/pages/dashboard/AgentsPage"

import {
  AIChatPage,
} from "@/pages/dashboard/AIChatPage"

import {
  ApprovalsPage,
} from "@/pages/dashboard/ApprovalsPage"

import {
  DashboardPage,
} from "@/pages/dashboard/DashboardPage"

import {
  KnowledgeBasePage,
} from "@/pages/dashboard/KnowledgeBasePage"

import {
  MCPToolsPage,
} from "@/pages/dashboard/MCPToolsPage"

import {
  OrchestratorPage,
} from "@/pages/dashboard/OrchestratorPage"

import {
  ProfilePage,
} from "@/pages/dashboard/ProfilePage"

import PromptTemplatesPage from "@/pages/dashboard/PromptTemplatesPage"

import {
  SettingsPage,
} from "@/pages/dashboard/SettingsPage"

import {
  WorkflowsPage,
} from "@/pages/dashboard/WorkflowsPage"

import {
  AgentAnalyticsPage,
} from "@/pages/analytics/AgentAnalyticsPage"

import {
  ProtectedRoute,
} from "@/routes/ProtectedRoute"

import {
  PublicRoute,
} from "@/routes/PublicRoute"

import {
  RoleRoute,
} from "@/routes/RoleRoute"

function App() {
  return (
    <Routes>
      {/* Default route */}
      <Route
        path="/"
        element={
          <Navigate
            to="/dashboard"
            replace
          />
        }
      />

      {/* Public authentication routes */}
      <Route element={<PublicRoute />}>
        <Route element={<AuthLayout />}>
          <Route
            path="/login"
            element={<LoginPage />}
          />

          <Route
            path="/register"
            element={<RegisterPage />}
          />

          <Route
            path="/forgot-password"
            element={
              <ForgotPasswordPage />
            }
          />

          <Route
            path="/reset-password"
            element={
              <ResetPasswordPage />
            }
          />
        </Route>
      </Route>

      {/* Protected application routes */}
      <Route element={<ProtectedRoute />}>
        <Route
          element={<DashboardLayout />}
        >
          {/* Routes available to every authenticated user */}
          <Route
            path="/dashboard"
            element={<DashboardPage />}
          />

          <Route
            path="/ai-chat"
            element={<AIChatPage />}
          />

          <Route
            path="/prompt-templates"
            element={
              <PromptTemplatesPage />
            }
          />

          <Route
            path="/knowledge-base"
            element={
              <KnowledgeBasePage />
            }
          />

          <Route
            path="/profile"
            element={<ProfilePage />}
          />

          {/* Admin, Manager, HR and Support routes */}
          <Route
            element={
              <RoleRoute
                allowedRoles={[
                  "Admin",
                  "Manager",
                  "HR",
                  "Support",
                ]}
              />
            }
          >
            <Route
              path="/orchestrator"
              element={
                <OrchestratorPage />
              }
            />

            <Route
              path="/agents"
              element={<AgentsPage />}
            />

            <Route
              path="/workflows"
              element={
                <WorkflowsPage />
              }
            />

            <Route
              path="/mcp-tools"
              element={
                <MCPToolsPage />
              }
            />

            <Route
              path="/approvals"
              element={
                <ApprovalsPage />
              }
            />

            <Route
              path="/analytics"
              element={
                <AgentAnalyticsPage />
              }
            />
          </Route>

          {/* Admin-only routes */}
          <Route
            element={
              <RoleRoute
                allowedRoles={[
                  "Admin",
                ]}
              />
            }
          >
            <Route
              path="/settings"
              element={
                <SettingsPage />
              }
            />
          </Route>
        </Route>
      </Route>

      {/* Unauthorized page */}
      <Route
        path="/unauthorized"
        element={
          <UnauthorizedPage />
        }
      />

      {/* Catch-all route */}
      <Route
        path="*"
        element={
          <NotFoundPage />
        }
      />
    </Routes>
  )
}

export default App