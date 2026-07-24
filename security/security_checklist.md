# Security Checklist

- [ ] Store secrets in GitHub/Kubernetes secret management
- [ ] Rotate refresh tokens and revoke reused tokens
- [ ] Use secure, HttpOnly, SameSite cookies
- [ ] Enforce password length and breach checks
- [ ] Configure strict CORS allow-list
- [ ] Enable rate limiting
- [ ] Add security headers
- [ ] Validate all requests with Pydantic
- [ ] Use HTTPS/TLS for every external and internal connection
- [ ] Encrypt database volumes at rest
- [ ] Run `pip-audit`, Bandit and container scans in CI
- [ ] Disable debug mode in production
- [ ] Log authentication and authorization failures
- [ ] Test backup restore procedures
