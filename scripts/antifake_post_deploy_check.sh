#!/usr/bin/env bash
# P-05 — post-deploy gate (no xcodebuild). Run on VPS after deploy_antifake_m1.sh.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "${ROOT}"

BASE="${ANTIFAKE_GATE_BASE:-http://127.0.0.1:8002}"
export ANTIFAKE_SMOKE_BASE="${ANTIFAKE_SMOKE_BASE:-${BASE}}"
export ANTIFAKE_GATE_BASE="${BASE}"

echo ">>> P-05 post-deploy: health"
curl -sf "${BASE}/api/health" | head -c 200
echo

echo ">>> P-05 post-deploy: smoke (poll jobs)"
ANTIFAKE_SMOKE_POLL_JOB=1 ./venv/bin/python3 docs/server/test_antifake_prod_smoke.py

echo ">>> P-05 post-deploy: gate af-11"
./venv/bin/python3 scripts/antifake_prod_gate_af11.py

echo ">>> P-05 post-deploy: worker verify"
./venv/bin/python3 scripts/antifake_verify_worker.py

echo ">>> P-05 post-deploy: ops alerts (informational)"
./venv/bin/python3 scripts/antifake_ops_alerts.py --check-all || true

echo ">>> P-05 post-deploy: ALL GREEN"
exit 0
