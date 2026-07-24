param(
    [Parameter(Mandatory=$true)]
    [string]$BackupFile
)

Get-Content $BackupFile | docker compose `
  -f docker\docker-compose.production.yml `
  exec -T postgres `
  psql -U postgres -d enterprise_ai

Write-Host "Restore completed from $BackupFile"
