Enterprise AI Workspace

AI-Powered Enterprise Automation Platform

Enterprise AI Workspace is a full-stack enterprise application builtwith React + TypeScript, FastAPI, PostgreSQL, and JWTAuthentication. It provides AI-powered workspace management, RBAC,administration tools, analytics, workflows, and an extensible AIarchitecture.

Sprint 1 -- Authentication

User Registration

User Login

JWT Authentication

Forgot Password

Reset Password

Logout

Protected Routes

Sprint 2 -- Enterprise Dashboard

Responsive Dashboard

Sidebar Navigation

Header Navigation

User Profile

Dark Mode

Dashboard Cards

Sprint 3 -- AI Workspace

AI Chat

Prompt Templates

Knowledge Base

AI Agents

Orchestrator

Workflows

Analytics

MCP Ready

Sprint 4 -- Administration

User Management

Admin Dashboard

User Statistics

Role Statistics

Permission Statistics

Recent Activity

Sprint 5 -- RBAC

Role Management

Create/Edit/Delete Roles

Permission Management

Create/Edit/Delete Permissions

Role Permission Assignment

Assign Permissions

Remove Permissions

Audit Logs

User Activity

Search

Filters

CSV Export

Installation

Backend

cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

Frontend

cd frontend
npm install
npm run dev

Author

D. Venkatesh