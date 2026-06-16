#!/usr/bin/env bash
# Level A auto-remediation: restart aladdin-backend after transient failures.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

BACKEND_SERVICE="${FAMILY_BACKEND_SERVICE:-aladdin-backend.service}"
SLEEP_SEC="${FAMILY_REMEDIATE_SLEEP_SEC:-5}"

echo ">>> family_auto_remediate: restarting ${BACKEND_SERVICE}"
systemctl restart "${BACKEND_SERVICE}"
sleep "${SLEEP_SEC}"
if ! systemctl is-active --quiet "${BACKEND_SERVICE}"; then
  echo "ERROR: ${BACKEND_SERVICE} not active after restart" >&2
  FAMILY_REMEDIATE_NOTIFY="${FAMILY_REMEDIATE_NOTIFY:-1}" \
    bash "${SCRIPT_DIR}/family_telegram_notify.sh" "ALADDIN family: restart FAILED — ${BACKEND_SERVICE} not active"
  exit 1
fi
echo ">>> family_auto_remediate: ${BACKEND_SERVICE} active"
