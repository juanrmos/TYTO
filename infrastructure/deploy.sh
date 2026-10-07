#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
ENV_FILE="${TYTO_ENV_FILE:-.env.production}"
test -f "$ENV_FILE" || { echo "Falta $ENV_FILE" >&2; exit 1; }
compose=(docker compose --env-file "$ENV_FILE" -f infrastructure/compose.production.yml)
if [[ -n "${1:-}" ]]; then
  git fetch origin --tags
  git checkout --detach "$1"
else
  git pull --ff-only
fi
if [[ -n "$("${compose[@]}" ps --status running -q db)" ]]; then
  bash infrastructure/backup.sh
fi
"${compose[@]}" config --quiet
"${compose[@]}" build stp sms init
"${compose[@]}" up -d --wait db sms
"${compose[@]}" run --rm init
"${compose[@]}" up -d --wait stp proxy
"${compose[@]}" exec -T stp python /app/scripts/smoke_test.py --base-url http://stp:8000 --sms-url http://sms:8001
echo "Despliegue verificado en red interna. Ejecutar smoke público y validar AWS Amplify Hosting."

