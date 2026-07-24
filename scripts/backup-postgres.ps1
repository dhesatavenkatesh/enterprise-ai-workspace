$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupDir = Join-Path $PSScriptRoot "..\backups"
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

docker compose -f docker\docker-compose.production.yml exec -T postgres `
  pg_dump -U postgres enterprise_ai `
  > "$backupDir\enterprise_ai-$timestamp.sql"

Write-Host "Backup created: $backupDir\enterprise_ai-$timestamp.sql"
