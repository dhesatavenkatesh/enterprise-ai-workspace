# Deployment Guide

1. Configure GitHub Environments: development, staging, production.
2. Add registry and Kubernetes credentials as repository secrets.
3. Replace `OWNER` and domain placeholders in `k8s/`.
4. Create production secrets outside Git.
5. Apply manifests:
   ```bash
   kubectl apply -f k8s/namespace.yaml
   kubectl apply -f k8s/
   ```
6. Verify:
   ```bash
   kubectl -n enterprise-ai get pods,svc,ingress
   kubectl -n enterprise-ai rollout status deployment/backend
   ```
