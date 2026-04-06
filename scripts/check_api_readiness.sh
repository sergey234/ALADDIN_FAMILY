#!/usr/bin/env bash
set -euo pipefail

# Simple external readiness check for ALADDIN API gateway.
# Verifies health, OpenAPI availability, critical routes presence, and absence of mock markers.
#
# Usage:
#   ./scripts/check_api_readiness.sh 149.154.65.180 8002
#
# Exit codes:
#   0 - all checks passed
#   1 - some checks failed

HOST="${1:-149.154.65.180}"
PORT="${2:-8002}"
BASE="http://${HOST}:${PORT}"
TMP_OPENAPI="/tmp/openapi_now.json"
FAILED=0

info() { printf "[INFO] %s\n" "$*"; }
ok()   { printf "[ OK ] %s\n" "$*"; }
err()  { printf "[ERR ] %s\n" "$*" 1>&2; FAILED=1; }

info "Checking health endpoint..."
HEALTH_JSON="$(curl -s -S -m 8 "${BASE}/api/health" || true)"
if [[ -n "${HEALTH_JSON}" ]]; then
  ok "Health responded: ${HEALTH_JSON}"
else
  err "Health check failed or empty response"
fi

info "Fetching OpenAPI spec..."
HTTP_CODE="$(curl -s -S -o "${TMP_OPENAPI}" -w "%{http_code}" -m 12 "${BASE}/openapi.json" || true)"
if [[ "${HTTP_CODE}" == "200" ]] && [[ -s "${TMP_OPENAPI}" ]]; then
  ok "OpenAPI available (200)"
else
  err "OpenAPI not available (code=${HTTP_CODE})"
fi

info "Checking critical routes in OpenAPI..."
python3 - <<'PY' "${TMP_OPENAPI}" || exit 1
import json, sys
p = sys.argv[1]
try:
    j = json.load(open(p, 'r', encoding='utf-8'))
except Exception as e:
    print(f"[ERR ] Failed to parse OpenAPI: {e}")
    sys.exit(1)
paths = j.get('paths', {})
checks = [
    '/api/reports/identity-theft/allow',
    '/api/reports/identity-theft/block',
    '/api/reports/privacy/tracker/whitelist',
    '/api/reports/privacy/location/allow',
    '/api/reports/privacy/cleanup/start',
    '/api/reports/dark-web/scan/start',
]
all_ok = True
for pth in checks:
    methods = sorted(list(paths.get(pth, {}).keys()))
    if not methods:
        print(f"[ERR ] Missing path in OpenAPI: {pth}")
        all_ok = False
    elif not set(methods) >= {'get','post'}:
        print(f"[ERR ] Path missing methods GET/POST: {pth} -> {methods}")
        all_ok = False
    else:
        print(f"[ OK ] {pth} -> {methods}")
if not all_ok:
    sys.exit(2)
PY
if [[ $? -eq 0 ]]; then
  ok "Critical routes present in OpenAPI"
else
  err "Critical routes verification failed"
fi

info "Probing public report endpoints (may return empty compat data before production routing enabled)..."
for ep in \
  "/api/reports/dark-web/stats" \
  "/api/reports/identity-theft/stats" \
  "/api/reports/privacy/tracker/stats" \
  "/api/reports/privacy/location/stats" \
  "/api/reports/privacy/cleanup/stats" \
; do
  RESP="$(curl -s -S -m 10 "${BASE}${ep}" || true)"
  if [[ -n "${RESP}" ]]; then
    ok "GET ${ep} -> ${#RESP} bytes"
  else
    err "GET ${ep} -> empty/failed"
  fi
done

info "Scanning responses for forbidden mock markers (prod hard rule)..."
FORBIDDEN_COUNT=0
for marker in 'sfm_mock' 'mock_fallback'; do
  if grep -E -q "${marker}" "${TMP_OPENAPI}" 2>/dev/null; then
    echo "[ERR ] Forbidden marker in OpenAPI: ${marker}"
    FORBIDDEN_COUNT=$((FORBIDDEN_COUNT+1))
  fi
done

# Additionally check a couple of live responses for markers (best-effort)
for ep in \
  "/api/reports/dark-web/stats" \
  "/api/reports/identity-theft/stats" \
; do
  BODY="$(curl -s -S -m 10 "${BASE}${ep}" || true)"
  if echo "${BODY}" | grep -E -q 'sfm_mock|mock_fallback'; then
    echo "[ERR ] Forbidden marker in ${ep} response"
    FORBIDDEN_COUNT=$((FORBIDDEN_COUNT+1))
  fi
done

if [[ "${FORBIDDEN_COUNT}" -gt 0 ]]; then
  err "Found ${FORBIDDEN_COUNT} forbidden mock markers"
else
  ok "No forbidden mock markers detected"
fi

if [[ "${FAILED}" -eq 0 ]]; then
  ok "API external readiness checks passed"
else
  err "API external readiness checks failed"
fi

exit "${FAILED}"

