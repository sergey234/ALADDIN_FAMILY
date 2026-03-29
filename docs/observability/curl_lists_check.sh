#!/usr/bin/env bash
set -euo pipefail
BASE="${BASE:-http://149.154.65.180:8002}"

echo "Checking list endpoints (limit=5)..."
curl -s -S -m 10 "$BASE/api/reports/dark-web/leaks?limit=5" | jq . | head -n 40 || true
curl -s -S -m 10 "$BASE/api/reports/privacy/location/requests?limit=5" | jq . | head -n 40 || true
curl -s -S -m 10 "$BASE/api/reports/privacy/tracker/top?limit=5" | jq . | head -n 40 || true
curl -s -S -m 10 "$BASE/api/reports/identity-theft/attempts?limit=5" | jq . | head -n 40 || true
curl -s -S -m 10 "$BASE/api/reports/privacy/cleanup/records?limit=5" | jq . | head -n 40 || true

echo "Done."

