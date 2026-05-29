#!/usr/bin/env bash
# VOICE-PREM-04 → 03 без зависания в чате: секреты из локального файла → VPS за один заход.
#
# 1) cp secrets/elevenlabs.env.example secrets/elevenlabs.local.env
# 2) Заполнить 4 строки (ключ + 3 voice id)
# 3) ./scripts/apply_elevenlabs_from_local_file.sh
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${1:-${LOCAL_ROOT}/secrets/elevenlabs.local.env}"
SSH_USER="${2:-root}"
HOST="${3:-149.154.65.180}"
SSH_KEY="${4:-${SSH_KEY_PATH:-$HOME/.ssh/aladdin_server}}"

if [[ ! -f "${ENV_FILE}" ]]; then
  echo "Missing ${ENV_FILE}" >&2
  echo "Run: ./scripts/voice_prem_04_03.sh  (needs secrets/elevenlabs.api_key)" >&2
  echo "Or: cp secrets/elevenlabs.env.example secrets/elevenlabs.local.env" >&2
  exit 1
fi

RECOMMENDED="${LOCAL_ROOT}/secrets/elevenlabs.recommended-voices.env"
if [[ -f "${RECOMMENDED}" ]]; then
  # shellcheck source=/dev/null
  source "${RECOMMENDED}"
fi

# shellcheck source=/dev/null
set -a
source "${ENV_FILE}"
set +a

export ELEVENLABS_API_KEY ELEVENLABS_VOICE_UNICORN ELEVENLABS_VOICE_GENIE ELEVENLABS_VOICE_ALADDIN
export ELEVENLABS_MODEL="${ELEVENLABS_MODEL:-eleven_flash_v2_5}"

"${SCRIPT_DIR}/configure_companion_neuro_tts_env.sh" "${SSH_USER}" "${HOST}" "${SSH_KEY}"
"${SCRIPT_DIR}/verify_companion_neuro_tts_voices.sh" "${SSH_USER}" "${HOST}" "${SSH_KEY}"

BASE="${VERIFY_BASE:-https://aladdin-ai.ru}"
export PREMIUM_TOKEN="$("${SCRIPT_DIR}/mint_premium_companion_jwt.sh")"
CODE=$(curl -sS -m 25 -o /tmp/companion_tts_probe.json -w "%{http_code}" -X POST "${BASE}/api/ai/companion/tts" \
  -H "Authorization: Bearer ${PREMIUM_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"text":"Привет","character_id":"genie","locale":"ru"}')
echo "TTS probe HTTP ${CODE}"
head -c 120 /tmp/companion_tts_probe.json 2>/dev/null; echo

if [[ "${CODE}" == "200" ]]; then
  "${SCRIPT_DIR}/prewarm_companion_tts_cache.sh" "${BASE}"
  echo "VOICE-PREM-04 + 03 OK"
else
  echo "TTS not 200 yet (check keys / voice ids). iOS still uses AVSpeech fallback." >&2
  exit 1
fi
