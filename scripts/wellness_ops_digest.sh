#!/usr/bin/env bash
# r100-1-15 — lightweight wellness ops digest (prod health + optional VPS logs).
# Usage:
#   ./scripts/wellness_ops_digest.sh
#   ./scripts/wellness_ops_digest.sh https://aladdin-ai.ru root 149.154.65.180 ~/.ssh/aladdin_server

set -euo pipefail

BASE="${1:-https://aladdin-ai.ru}"
SSH_USER="${2:-}"
HOST="${3:-}"
SSH_KEY="${4:-}"

echo "=== Wellness ops digest $(date -u +%Y-%m-%dT%H:%M:%SZ) ==="
echo "Base: ${BASE}"

if command -v curl >/dev/null 2>&1; then
  for path in "/health" "/api/wellness/health" "/api/wellness/hub/skeleton?locale=ru"; do
    code=$(curl -sS -o /dev/null -w "%{http_code}" "${BASE}${path}" 2>/dev/null || echo "000")
    echo "HTTP ${code} ${path}"
  done
else
  echo "curl not found — skip HTTP probes"
fi

if [[ -n "${SSH_USER}" && -n "${HOST}" ]]; then
  SSH_OPTS=(-o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=12)
  [[ -n "${SSH_KEY}" ]] && SSH_OPTS+=(-i "${SSH_KEY}")
  echo "--- VPS log sample (wellness_pillar_drift, 24h) ---"
  ssh "${SSH_OPTS[@]}" "${SSH_USER}@${HOST}" \
    "journalctl -u aladdin-backend.service --since '24 hours ago' 2>/dev/null | grep -c wellness_pillar_drift || echo 0" \
    || echo "ssh failed"
fi

echo "=== Done ==="
