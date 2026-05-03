#!/usr/bin/env bash
# pc-18: смоук родительского API (нужны curl и jq).
#   export ALADDIN_API_BASE=https://aladdin-ai.ru   # или http://host:8002
#   export ALADDIN_JWT='<access_token>'
#   export ALADDIN_CHILD_ID=''   # опционально, childId query
set -euo pipefail

BASE="${ALADDIN_API_BASE:-}"
TOKEN="${ALADDIN_JWT:-}"
CHILD="${ALADDIN_CHILD_ID:-}"

if [[ -z "$BASE" || -z "$TOKEN" ]]; then
  echo "Set ALADDIN_API_BASE and ALADDIN_JWT" >&2
  exit 1
fi

Q=""
if [[ -n "$CHILD" ]]; then
  Q="?childId=${CHILD}"
fi

hdr=(-H "Authorization: Bearer ${TOKEN}" -H "Accept: application/json")

echo "== GET /api/parental-control/stats${Q}"
curl -sS -m 20 "${hdr[@]}" "${BASE}/api/parental-control/stats${Q}" | jq '.reports // .' | head -c 2000
echo ""

echo "== GET /api/parental-control/monitoring/detail${Q}"
DETAIL_JSON="$(curl -sS -m 20 "${hdr[@]}" "${BASE}/api/parental-control/monitoring/detail${Q}")"
echo "${DETAIL_JSON}" | jq '.summary, (.top_sites|length), (.suspicious|length)' 2>/dev/null || echo "${DETAIL_JSON}" | head -c 1500
echo ""

# FastAPI контракт: корневые snake_case поля. Envelope шлюза: function + пустой result (см. docs/PARENTAL_MONITORING_DETAIL_GATEWAY_PLAN.md).
if echo "${DETAIL_JSON}" | jq -e '.top_sites != null' >/dev/null 2>&1; then
  echo "smoke: monitoring/detail contract OK (has top_sites)"
elif echo "${DETAIL_JSON}" | jq -e '.function != null' >/dev/null 2>&1; then
  msg="smoke: ERROR monitoring/detail is gateway/mock envelope (has function, missing top_sites). Fix nginx/SFM passthrough to FastAPI. Doc: docs/PARENTAL_MONITORING_DETAIL_GATEWAY_PLAN.md"
  if [[ "${ALADDIN_ALLOW_GATEWAY_ENVELOPE:-}" == "1" ]]; then
    echo "WARN: ${msg} (ALADDIN_ALLOW_GATEWAY_ENVELOPE=1 — exit 0)" >&2
  else
    echo "${msg}" >&2
    exit 1
  fi
else
  echo "smoke: WARN monitoring/detail unexpected JSON (no top_sites, no function)" >&2
fi

echo "== GET /api/parental-control/reports/weekly${Q}"
curl -sS -m 20 "${hdr[@]}" "${BASE}/api/parental-control/reports/weekly${Q}" | jq 'if type=="array" then length else . end' 2>/dev/null || true
echo ""

echo "== GET /api/parental/bypass/stats${Q}"
curl -sS -m 20 "${hdr[@]}" "${BASE}/api/parental/bypass/stats${Q}" | jq '.' 2>/dev/null || curl -sS -m 20 "${hdr[@]}" "${BASE}/api/parental/bypass/stats${Q}"
echo ""

echo "== POST /api/parental-control/monitoring/events (sample url_visit; JWT должен быть ребёнка с числовым user_id)"
curl -sS -m 20 "${hdr[@]}" -H "Content-Type: application/json" \
  -d '{"events":[{"kind":"url_visit","payload":{"url_sha256":"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa","site":"example.com","visits":1}}]}' \
  "${BASE}/api/parental-control/monitoring/events" | jq '.' 2>/dev/null || true
echo ""
echo "Done."
