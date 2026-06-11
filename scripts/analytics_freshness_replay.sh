#!/usr/bin/env bash
# Replay POST по 4 доменам freshness (identity/tracker/location/cleanup) + verify metrics.
set -euo pipefail

BASE="${1:-http://127.0.0.1:8002}"
STAMP="$(date +%s)"

fail() { echo "FAIL: $*" >&2; exit 1; }
ok() { echo "OK: $*"; }

echo "=== analytics freshness replay → ${BASE} ==="

IDENTITY_ID="$(sudo -u postgres psql -d aladdin_db -At -c "SELECT id::text FROM identity.identity_attempts ORDER BY timestamp DESC LIMIT 1;" 2>/dev/null | tr -d '[:space:]')"
LOCATION_ID="$(sudo -u postgres psql -d aladdin_db -At -c "SELECT id::text FROM location.location_requests ORDER BY timestamp DESC LIMIT 1;" 2>/dev/null | tr -d '[:space:]')"
TRACKER_NAME="ops-replay-tracker-${STAMP}"

[[ -n "${IDENTITY_ID}" ]] || fail "no identity.identity_attempts row"
[[ -n "${LOCATION_ID}" ]] || fail "no location.location_requests row"

post() {
  local path="$1" body="$2" label="$3"
  local code body_out
  body_out=$(curl -sS -m 20 -w "\n%{http_code}" -X POST "${BASE}${path}" \
    -H "Content-Type: application/json" -d "${body}")
  code=$(echo "${body_out}" | tail -1)
  echo "  ${label}: HTTP ${code} $(echo "${body_out}" | head -1 | cut -c1-120)"
  [[ "${code}" == "200" ]] || fail "${label} http ${code}"
}

post "/api/reports/identity-theft/allow" "{\"attemptId\":\"${IDENTITY_ID}\"}" "identity"
post "/api/reports/privacy/location/allow" "{\"requestId\":\"${LOCATION_ID}\"}" "location"
post "/api/reports/privacy/tracker/whitelist" "{\"trackerName\":\"${TRACKER_NAME}\"}" "tracker"
post "/api/reports/privacy/cleanup/start" '{"categories":["cache","logs"]}' "cleanup"

echo "=== DB analytics_freshness ==="
sudo -u postgres psql -d aladdin_db -c \
  "SELECT domain, last_event_at, round(extract(epoch from (now()-last_event_at))/60,1) AS age_min FROM analytics_freshness ORDER BY domain;"

echo "=== wait metrics scrape (35s) ==="
sleep 35

echo "=== Prometheus gauges ==="
curl -sS -m 8 "${BASE}/metrics" | grep 'aladdin_analytics_freshness_seconds{' | grep -E 'domain="(identity|tracker|location|cleanup)"' || true

echo "=== prom active alerts (freshness) ==="
curl -sS -m 8 'http://127.0.0.1:9090/api/v1/alerts' | python3 - <<'PY'
import json, sys
data = json.load(sys.stdin).get("data", {}).get("alerts", [])
fresh = [a for a in data if a.get("labels", {}).get("alertname") == "AladdinNoFreshDataByDomain"]
if not fresh:
    print("OK: no active AladdinNoFreshDataByDomain alerts")
else:
    for a in fresh:
        lbl = a.get("labels", {})
        print("WARN firing:", lbl.get("domain"), a.get("state"))
PY

ok "replay complete"
