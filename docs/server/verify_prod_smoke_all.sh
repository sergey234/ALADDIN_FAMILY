#!/usr/bin/env bash
# Aggregate prod smoke gate — SFM + antifake contract (af-smoke-07)
set -euo pipefail

BACKEND="${ALADDIN_BACKEND_PATH:-/opt/aladdin-backend}"
cd "$BACKEND"
export ANTIFAKE_SMOKE_BASE="${ANTIFAKE_SMOKE_BASE:-http://127.0.0.1:8002}"
export ANTIFAKE_SMOKE_SFM_BASE="${ANTIFAKE_SMOKE_SFM_BASE:-http://127.0.0.1:8003}"
PYTHON="${BACKEND}/venv/bin/python3"
FAILURES=0

echo "== SFM prod smoke =="
if bash "${BACKEND}/docs/server/sfm_prod_smoke.sh"; then
  echo "PASS sfm_prod_smoke"
else
  echo "FAIL sfm_prod_smoke — attempting conditional remediate"
  if bash "${BACKEND}/docs/server/sfm_auto_remediate.sh"; then
    bash "${BACKEND}/docs/server/sfm_prod_smoke.sh" || FAILURES=$((FAILURES + 1))
  else
    FAILURES=$((FAILURES + 1))
  fi
fi

echo "== Antifake prod smoke =="
if "$PYTHON" docs/server/test_antifake_prod_smoke.py; then
  echo "PASS test_antifake_prod_smoke"
else
  FAILURES=$((FAILURES + 1))
fi

if [[ "$FAILURES" -gt 0 ]]; then
  echo "verify_prod_smoke_all: FAIL ($FAILURES)"
  exit 1
fi

echo "verify_prod_smoke_all: PASS"
exit 0
