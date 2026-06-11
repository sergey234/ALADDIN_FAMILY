#!/usr/bin/env bash
# Server-side smoke = задачи 1.4 + проверка llm_path (без Xcode).
# Usage: ./hermes_harness_smoke_api.sh [base_url]
set -euo pipefail

BASE="${1:-http://127.0.0.1:8002}"
DEVICE_ID="hermes-smoke-$(date +%s)"
LOG="${COMPANION_LLM_METRICS_LOG:-/var/log/aladdin-backend/companion_llm.log}"
FORBIDDEN=("Я отвечаю по базе знаний" "187 функций" "1074 функций")

fail() { echo "FAIL: $*" >&2; exit 1; }
ok() { echo "OK: $*"; }

echo "=== [1] Health ==="
curl -sS -m 8 "${BASE}/api/health" | grep -q '"status"' || fail "health"
ok "health"

echo "=== [2] JWT (child companion) ==="
RESP=$(curl -sS -m 15 -X POST "${BASE}/api/auth/register-device" \
  -H "Content-Type: application/json" \
  -d "{\"deviceId\":\"${DEVICE_ID}\",\"deviceType\":\"ios\"}")
TOKEN=$(echo "${RESP}" | python3 -c "import json,sys; print(json.load(sys.stdin)['access_token'])")
AUTH=(-H "Authorization: Bearer ${TOKEN}" -H "Content-Type: application/json")
ok "jwt"

check_response() {
  local label="$1"
  local body="$2"
  local text
  text=$(echo "${body}" | python3 -c "import json,sys; print(json.load(sys.stdin).get('response','')[:300])")
  local tools
  tools=$(echo "${body}" | python3 -c "import json,sys; print(json.load(sys.stdin).get('tools_used',[]))")
  for f in "${FORBIDDEN[@]}"; do
    if echo "${text}" | grep -qF "${f}"; then
      fail "${label}: SFM template detected (${f})"
    fi
  done
  if [[ -z "${text}" ]]; then
    fail "${label}: empty response"
  fi
  echo "  tools_used: ${tools}"
  echo "  response: ${text:0:120}..."
  if echo "${tools}" | grep -qE 'openrouter|hermes'; then
    ok "${label} live LLM path"
  else
    echo "WARN: ${label} no openrouter/hermes in tools_used (may be kb_rag)"
  fi
}

echo "=== [3] AI Assistant — тарифы ==="
A_BODY=$(curl -sS -m 90 "${AUTH[@]}" -X POST "${BASE}/api/ai/assistant/chat" \
  -d '{"message":"Какие тарифы ALADDIN?","context":"general","stream":false}')
check_response "AI Assistant" "${A_BODY}"

echo "=== [4] Companion — сказка ==="
C_BODY=$(curl -sS -m 90 "${AUTH[@]}" -X POST "${BASE}/api/ai/companion/chat" \
  -d '{"message":"Расскажи короткую сказку про единорога","character_id":"unicorn","chat_mode":"fast","stream":false}')
check_response "Companion" "${C_BODY}"

echo "=== [5] companion_llm.log tail ==="
if [[ -f "${LOG}" ]]; then
  tail -3 "${LOG}" || true
  if tail -20 "${LOG}" | grep -q 'openrouter_direct\|"llm_path": "openrouter_direct"'; then
    ok "log has openrouter_direct"
  elif tail -20 "${LOG}" | grep -q 'hermes'; then
    ok "log has hermes"
  else
    echo "WARN: no openrouter_direct in last 20 log lines yet"
  fi
else
  echo "WARN: log file missing ${LOG}"
fi

echo "=== HARNESS SMOKE PASS ==="
