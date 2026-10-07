#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
umask 077
mkdir -p backups
file="backups/tyto-$(date -u +%Y%m%dT%H%M%SZ).dump"
docker compose --env-file "${TYTO_ENV_FILE:-.env.production}" -f infrastructure/compose.production.yml \
  exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' > "$file"
test -s "$file"
echo "Respaldo creado: $file"
