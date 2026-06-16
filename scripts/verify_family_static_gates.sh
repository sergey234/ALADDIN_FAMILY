#!/usr/bin/env bash
# Pre-deploy static gates for family auth + roster contracts.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
cd "${ROOT}"

python3 scripts/family_client_tamper_guard_smoke.py
python3 scripts/family_auth_static_guard_smoke.py
echo "verify_family_static_gates: OK"
