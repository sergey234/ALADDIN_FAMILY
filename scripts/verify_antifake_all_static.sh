#!/usr/bin/env bash
# Master static gate — all antifake code checks without xcodebuild / simulator.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== antifake all static gates ==="
bash scripts/verify_antifake_q_static.sh
bash scripts/verify_antifake_device_readiness.sh
bash scripts/verify_antifake_open_tasks_code.sh
python3 scripts/verify_antifake_release_readiness.py
python3 scripts/verify_antifake_marketing_claims.py
echo "=== OK — all antifake static gates passed (device QA + xcodebuild remain manual) ==="
