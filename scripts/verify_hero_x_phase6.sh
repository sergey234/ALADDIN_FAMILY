#!/usr/bin/env bash
# hero-x phase 6 — full local verification before/after deploy
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo ">>> [1/6] Wellness + companion l10n"
python3 scripts/check_wellness_l10n.py

echo ">>> [2/6] Companion pytest (all test_companion_*)"
./scripts/run_companion_tests.sh

echo ">>> [3/6] Parametrize count gate (hero-x-60, min 40)"
PYTHONPATH=. python3 scripts/count_companion_parametrize.py --min 40

echo ">>> [4/6] Golden set scorer (hero-x-07, ≥95%)"
PYTHONPATH=. python3 -m pytest Tests/test_companion_golden_scorer.py -q

echo ">>> [5/6] Ethics hard gate (hero-x-63)"
PYTHONPATH=. python3 -m pytest Tests/test_companion_ethics_gate.py -q

echo ">>> [6/6] Metrics module import"
PYTHONPATH=. python3 -c "
from security.services.ai_platform.companion_analytics import (
    COMPANION_EVENT_HUMOR_INJECTED,
    COMPANION_EVENT_WISDOM_USED,
    COMPANION_EVENT_GUARD_TRIGGERED,
)
assert COMPANION_EVENT_HUMOR_INJECTED == 'humor_injected'
print('OK metrics events')
"

echo ">>> [7/7] Vedic secular gate (hero-x-14)"
python3 scripts/verify_vedic_secular_gate.py

echo ""
echo ">>> hero-x phase 6 local gate: ALL PASSED"
