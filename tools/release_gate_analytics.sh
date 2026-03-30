#!/usr/bin/env bash
set -euo pipefail

echo "[release-gate] Running analytics components contract tests..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

export ALADDIN_API_BASE="${ALADDIN_API_BASE:-https://aladdin-ai.ru}"
python3 "$SCRIPT_DIR/contract_tests_components.py"
echo "[release-gate] PASS"

