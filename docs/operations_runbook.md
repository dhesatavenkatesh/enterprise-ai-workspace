# Operations Runbook

## Health Checks
- Backend: `/health`
- Metrics: `/metrics`
- Frontend: `/health`

## Common Commands
```bash
kubectl -n enterprise-ai get pods
kubectl -n enterprise-ai logs deployment/backend --tail=200
kubectl -n enterprise-ai rollout restart deployment/backend
kubectl -n enterprise-ai rollout undo deployment/backend
```

## Incident Priorities
- P1: Total outage, security breach, data loss
- P2: Major feature unavailable
- P3: Partial degradation

## Alert Actions
- High CPU: inspect hot endpoints and scale replicas
- Failed pods: inspect events and logs
- API errors: check deployment, database and external AI provider
- Queue backlog: scale Celery workers and inspect failed tasks
