# Disaster Recovery

## Targets
- RTO: 4 hours
- RPO: 1 hour

## Backup Schedule
- PostgreSQL: hourly incremental/WAL and nightly full backup
- Redis: AOF enabled and nightly snapshot
- ChromaDB: nightly volume snapshot
- Configuration: version controlled; secrets backed up in secret manager

## Restore Process
1. Provision replacement infrastructure.
2. Restore PostgreSQL latest full backup and replay WAL.
3. Restore Redis AOF/RDB.
4. Restore ChromaDB persistent volume snapshot.
5. Deploy the last known-good application image.
6. Run smoke tests and data integrity checks.
7. Re-enable traffic.

## Rollback Strategy
Redeploy the previous immutable image tag and reverse incompatible database migrations.

## Failover Plan
Route traffic to the secondary environment after health checks fail and approval is given.
