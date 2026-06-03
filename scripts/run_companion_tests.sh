#!/usr/bin/env bash
# Companion pytest gate — hero-x / CI parity (requires python-multipart)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if ! python3 -c "import multipart" 2>/dev/null; then
  echo "Installing Tests/requirements-test.txt ..."
  python3 -m pip install -r Tests/requirements-test.txt -q
fi
export PYTHONPATH=.
python3 -m pytest Tests/test_companion_*.py -q "$@"
echo ">>> Golden + ethics gate"
python3 -m pytest Tests/test_companion_golden_scorer.py Tests/test_companion_ethics_gate.py -q
python3 scripts/count_companion_parametrize.py --min 40
