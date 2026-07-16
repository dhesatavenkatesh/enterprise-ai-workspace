# Enterprise AI Workspace

A secure enterprise workspace built with React, FastAPI, PostgreSQL, Redis, JWT authentication, role-based access control, and Docker.

## Architecture

```text
React + TypeScript + Vite
          |
Axios + TanStack Query
          |
FastAPI
          |
JWT Authentication + RBAC
          |
PostgreSQL + Redis
```

## Features

- User registration and login
- JWT access tokens
- Refresh-token rotation
- Session validation
- Secure logout
- Role-based access control
- Permission-based authorization
- Responsive dashboard
- Protected frontend routes
- Automatic token refresh
- Global API error handling
- PostgreSQL persistence
- Redis service
- Docker Compose environment

## Roles

- Admin
- HR
- Employee
- Manager
- Support

## Project Structure

```text
enterprise-ai-workspace/
├── backend/
├── frontend/
├── database/
├── docker/
├── docs/
├── scripts/
├── k8s/
├── docker-compose.yml
└── README.md
```

## Backend Setup

```powershell
cd backend
python -m venv venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
python -m app.database.seed
python -m app.database.seed_permissions
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

## Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

Frontend:

```text
http://localhost:5173
```

## Docker Setup

Create `.env.docker` and run:

```powershell
docker compose --env-file .env.docker up --build
```

Services:

```text
Frontend:   http://localhost:5173
Backend:    http://localhost:8000
Swagger:    http://localhost:8000/docs
PostgreSQL: localhost:5432
Redis:      localhost:6379
```

## Main Authentication APIs

```text
POST /api/auth/register
POST /api/auth/login
POST /api/auth/logout
POST /api/auth/refresh
GET  /api/auth/me
```

## RBAC Test APIs

```text
GET /api/admin/test
GET /api/hr/test
GET /api/employee/test
GET /api/manager/test
GET /api/support/test
GET /api/chat/test
```

## Frontend Build

```powershell
cd frontend
npm run lint
npm run build
```

## Stop Docker

```powershell
docker compose --env-file .env.docker down
```

Delete volumes:

```powershell
docker compose --env-file .env.docker down -v
```

## Branch Strategy

```text
feature/* → develop → main
```

Branches:

```text
main
develop
feature/auth
feature/frontend
feature/backend
```

## Security

Do not commit:

```text
.env
.env.docker
JWT secrets
Database passwords
Access tokens
Refresh tokens
```