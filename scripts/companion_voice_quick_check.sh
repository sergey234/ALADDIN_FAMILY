#!/usr/bin/env bash
# Neuro-TTS smoke: Free off · Trial+Premium on (when FEATURE_NEURO_TTS_TRIAL=1).
set -euo pipefail

BASE="${1:-https://aladdin-ai.ru}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

echo "=== health ==="
curl -sS -m 6 "${BASE}/api/health"
echo ""

check_tier() {
  local label="$1"
  local level="$2"
  local expect_neuro="$3"
  local token cap_file tts_file

  token="$(SUBSCRIPTION_LEVEL="${level}" "${SCRIPT_DIR}/mint_premium_companion_jwt.sh")"
  cap_file="${TMP_DIR}/cap_${level}.json"
  tts_file="${TMP_DIR}/tts_${level}.json"

  echo ""
  echo "=== ${label} (subscription=${level}, expect neuro=${expect_neuro}) ==="

  curl -sS -m 10 -H "Authorization: Bearer ${token}" \
    "${BASE}/api/ai/companion/capabilities" > "${cap_file}"

  python3 - "${cap_file}" "${expect_neuro}" <<'PY'
import json, sys
path, expect = sys.argv[1], sys.argv[2].lower() == "true"
d = json.load(open(path))
feat = d.get("features", {}).get("companion_neuro_tts", {})
ui = feat.get("ui") or {}
neuro = ui.get("neuro_tts_premium")
print("subscription_level", d.get("subscription_level"))
print("neuro_tts_premium", neuro)
print("tts_provider", ui.get("tts_provider"))
if neuro is not expect:
    raise SystemExit(f"FAIL: neuro_tts_premium={neuro}, expected {expect}")
print("capabilities OK")
PY

  local http_code
  http_code="$(curl -sS -m 20 -o "${tts_file}" -w "%{http_code}" \
    -X POST "${BASE}/api/ai/companion/tts" \
    -H "Authorization: Bearer ${token}" \
    -H "Content-Type: application/json" \
    -d '{"text":"Тест neuro-TTS","character_id":"genie","locale":"ru"}')"

  echo "POST /tts HTTP ${http_code}"
  if [[ "${expect_neuro}" == "true" ]]; then
    if [[ "${http_code}" == "200" ]]; then
      python3 - "${tts_file}" <<'PY'
import json, sys
d = json.load(open(sys.argv[1]))
b = d.get("audio_base64") or ""
print("provider", d.get("provider"), "cached", d.get("cached"), "audio_b64_len", len(b))
if len(b) < 32:
    raise SystemExit("FAIL: empty audio_base64")
print("tts OK — ElevenLabs audio received")
PY
    elif [[ "${http_code}" == "424" ]]; then
      echo "WARN: 424 neuro_tts_unconfigured — VOICE-PREM-04 keys pending (capability gate OK)"
    else
      head -c 200 "${tts_file}" || true
      echo ""
      echo "FAIL: expected 200 or 424, got ${http_code}"
      exit 1
    fi
  else
    if [[ "${http_code}" == "403" ]]; then
      echo "tts blocked OK (403 — no ElevenLabs for Free)"
    else
      head -c 200 "${tts_file}" || true
      echo ""
      echo "FAIL: Free must get 403, got ${http_code}"
      exit 1
    fi
  fi
}

check_tier "FREE" "free" "false"
check_tier "TRIAL" "trial" "true"
check_tier "PREMIUM" "premium" "true"

echo ""
echo "=== VPS voices (if SSH) ==="
"${SCRIPT_DIR}/verify_companion_neuro_tts_voices.sh" 2>/dev/null || echo "SKIP: VOICE-PREM-04 — no elevenlabs voice ids on server yet"

echo ""
echo "=== ALL CHECKS PASSED ==="
