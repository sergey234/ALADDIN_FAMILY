#!/usr/bin/env bash
# HIBP API key on VPS — secrets NOT in git.
#
# Enables real email breach lookup on POST /api/reports/dark-web/scan/fast.
# Paid subscription required for real email lookup (Core from ~$4.39/mo):
# https://haveibeenpwned.com/Subscription — key from dashboard after purchase.
#
# Usage (do NOT paste the key into chat — run locally):
#   export HIBP_API_KEY="your-key-from-hibp"
#   ./scripts/configure_hibp_api_key_prod.sh [ssh_user] [host] [ssh_key]
#
set -euo pipefail

SSH_USER="${1:-root}"
HOST="${2:-149.154.65.180}"
SSH_KEY="${3:-${SSH_KEY_PATH:-$HOME/.ssh/aladdin_server}}"
REMOTE_ROOT="/opt/aladdin-backend"
SECRETS_FILE="${REMOTE_ROOT}/secrets/hibp.env"

if [[ -z "${HIBP_API_KEY:-}" ]]; then
  echo "Set HIBP_API_KEY in your shell (from https://haveibeenpwned.com/API/Key), then re-run." >&2
  echo "Example: HIBP_API_KEY='...' $0" >&2
  exit 1
fi

# HIBP keys are UUID-like; reject obvious placeholders from docs.
if [[ "${HIBP_API_KEY}" == *"your"* ]] || [[ "${#HIBP_API_KEY}" -lt 20 ]]; then
  echo "HIBP_API_KEY looks invalid (too short or placeholder). Use the key from haveibeenpwned.com." >&2
  exit 1
fi

echo "=== Local: verify key with HIBP (no email leaked) ==="
HTTP=$(curl -sS -m 15 -o /dev/null -w "%{http_code}" \
  -H "hibp-api-key: ${HIBP_API_KEY}" \
  -H "User-Agent: ALADDIN-Security-iOS/1.0" \
  "https://haveibeenpwned.com/api/v3/breachedaccount/account-exists-but-wont-be-found@hibp-integration-tests.com")
case "${HTTP}" in
  404|200) echo "HIBP key OK (HTTP ${HTTP})" ;;
  401) echo "HIBP rejected key (HTTP 401). Check key at haveibeenpwned.com/API/Key" >&2; exit 1 ;;
  *) echo "HIBP unexpected HTTP ${HTTP} — continuing anyway" ;;
esac

SSH_OPTS=(-o BatchMode=yes -o StrictHostKeyChecking=no -o IdentitiesOnly=yes)
[[ -n "${SSH_KEY}" ]] && SSH_OPTS+=(-i "${SSH_KEY}")

ssh_r() { ssh "${SSH_OPTS[@]}" "${SSH_USER}@${HOST}" "$@"; }

ssh_r "set -e
  mkdir -p ${REMOTE_ROOT}/secrets
  chmod 700 ${REMOTE_ROOT}/secrets
  umask 077
  cat > ${SECRETS_FILE} <<EOF
HIBP_API_KEY=${HIBP_API_KEY}
EOF
  chmod 600 ${SECRETS_FILE}
  DROPIN=/etc/systemd/system/aladdin-backend.service.d/65-hibp-env.conf
  cat > \${DROPIN} <<'DROPINEOF'
[Service]
EnvironmentFile=/opt/aladdin-backend/secrets/hibp.env
DROPINEOF
  systemctl daemon-reload
  systemctl restart aladdin-backend.service
  sleep 2
  systemctl is-active aladdin-backend.service

  cd ${REMOTE_ROOT}
  ./venv/bin/python3 - <<'PY'
import os
from pathlib import Path

for line in Path('/opt/aladdin-backend/secrets/hibp.env').read_text().splitlines():
    line = line.strip()
    if not line or line.startswith('#') or '=' not in line:
        continue
    k, v = line.split('=', 1)
    os.environ[k.strip()] = v.strip().strip('\"').strip(\"'\")

from security.api.dark_web_scan_service import _hibp_api_key
val = _hibp_api_key()
print('server _hibp_api_key:', 'OK len=' + str(len(val)) if val else 'EMPTY')
PY
"

echo "OK: HIBP on ${HOST} (${SECRETS_FILE} + systemd drop-in 65-hibp-env.conf)"
echo "Smoke (on server): fast scan with a known pwned test email from your account — rate limits apply."
