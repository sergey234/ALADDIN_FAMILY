#!/usr/bin/env bash
# Этап 5 (минимум): публичный URL не должен отдавать SFM-envelope для monitoring/detail.
# Без JWT ожидается 403 + JSON с detail (FastAPI). Envelope = exit 1.
# Использование: ./tools/ci_check_parental_monitoring_detail_public.sh [BASE_URL]
set -euo pipefail
BASE="${1:-https://aladdin-ai.ru}"
URL="${BASE}/api/parental-control/monitoring/detail?childId=MEM_B6DCC7194068"
BODY="$(curl -sS -m 15 "${URL}")"
if echo "${BODY}" | jq -e '.function != null' >/dev/null 2>&1; then
  echo "FAIL: gateway/SFM envelope still returned for ${URL}" >&2
  echo "${BODY}" >&2
  exit 1
fi
if ! echo "${BODY}" | jq -e '.detail != null' >/dev/null 2>&1; then
  echo "FAIL: expected FastAPI body with .detail (401/403), got:" >&2
  echo "${BODY}" >&2
  exit 1
fi
echo "OK: no envelope; FastAPI-style rejection without JWT."
