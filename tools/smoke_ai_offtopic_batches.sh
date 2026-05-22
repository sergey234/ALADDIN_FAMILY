#!/usr/bin/env bash
# R4.1: прогон 100 off-topic батчами по 10 (~7–12 мин на батч на проде).
set -euo pipefail
BACKEND="${ALADDIN_BACKEND_ROOT:-/opt/aladdin-backend}"
PY="${BACKEND}/venv/bin/python3"
export ALADDIN_API_BASE="${ALADDIN_API_BASE:-http://127.0.0.1:8002}"
export AI_OFFTOPIC_TIMEOUT="${AI_OFFTOPIC_TIMEOUT:-75}"

if [[ -z "${ALADDIN_TEST_JWT:-}" ]]; then
  echo "Minting JWT via smoke_ai_offtopic100_prod.py (batch $1 only)..."
  export AI_OFFTOPIC_BATCH="${1:-1}"
  exec "$PY" "${BACKEND}/tools/smoke_ai_offtopic100_prod.py"
fi

batch="${1:-}"
if [[ -z "$batch" ]]; then
  echo "Usage: $0 <1-10>   # or set ALADDIN_TEST_JWT and run each batch"
  echo "       $0 all      # all 10 batches sequentially"
  exit 1
fi

if [[ "$batch" == "all" ]]; then
  failed=0
  for b in $(seq 1 10); do
    echo "======== batch $b/10 ========"
    export AI_OFFTOPIC_BATCH="$b"
    if ! "$PY" "${BACKEND}/tools/smoke_ai_offtopic100.py"; then
      failed=$((failed + 1))
    fi
  done
  echo "OFFTOPIC_BATCHES_DONE failed_batches=$failed/10"
  exit "$([[ $failed -eq 0 ]] && echo 0 || echo 1)"
fi

export AI_OFFTOPIC_BATCH="$batch"
exec "$PY" "${BACKEND}/tools/smoke_ai_offtopic100.py"
