#!/usr/bin/env bash
# Быстрая диагностика голоса (таймауты, без зависаний). ~15 сек.
set -euo pipefail

BASE="${1:-https://aladdin-ai.ru}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== health ==="
curl -sS -m 6 "${BASE}/api/health"
echo ""

echo "=== premium mint (SSH, <=10s) ==="
export PREMIUM_TOKEN="$("${SCRIPT_DIR}/mint_premium_companion_jwt.sh")"
echo "token_len=${#PREMIUM_TOKEN}"

echo "=== capabilities ==="
curl -sS -m 10 -H "Authorization: Bearer ${PREMIUM_TOKEN}" \
  "${BASE}/api/ai/companion/capabilities" | python3 -c "
import json,sys
d=json.load(sys.stdin)
n=d['features']['companion_neuro_tts']
print('subscription_level', d.get('subscription_level'))
print('neuro_tts_premium', n['ui'].get('neuro_tts_premium'))
print('tts_provider', n['ui'].get('tts_provider'))
"

echo "=== tts probe (genie) ==="
curl -sS -m 20 -w "\nHTTP %{http_code}\n" -X POST "${BASE}/api/ai/companion/tts" \
  -H "Authorization: Bearer ${PREMIUM_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"text":"Тест","character_id":"genie","locale":"ru"}' | head -c 200
echo ""

echo "=== VPS voices (if SSH) ==="
"${SCRIPT_DIR}/verify_companion_neuro_tts_voices.sh" 2>/dev/null || echo "SKIP: no elevenlabs.env on server (VOICE-PREM-04)"
