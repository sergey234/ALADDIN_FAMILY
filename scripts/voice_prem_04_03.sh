#!/usr/bin/env bash
# VOICE-PREM-04 → 03: bootstrap voices → VPS → prewarm → smoke
#
# Требуется ElevenLabs API key:
#   echo 'sk_...' > secrets/elevenlabs.api_key && chmod 600 secrets/elevenlabs.api_key
#
# Usage:
#   ./scripts/voice_prem_04_03.sh
#   ./scripts/voice_prem_04_03.sh https://aladdin-ai.ru
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BASE="${1:-https://aladdin-ai.ru}"

cd "${LOCAL_ROOT}"

echo "=== VOICE-PREM-04: bootstrap 3 hero voices ==="
python3 "${SCRIPT_DIR}/bootstrap_elevenlabs_voices.py"

echo ""
echo "=== VOICE-PREM-04: deploy to VPS ==="
"${SCRIPT_DIR}/apply_elevenlabs_from_local_file.sh"

echo ""
echo "=== Neuro-TTS smoke (Free / Trial / Premium) ==="
"${SCRIPT_DIR}/companion_voice_quick_check.sh" "${BASE}"

echo ""
echo "=== VOICE-PREM-03: extra prewarm (trial JWT, all RU greetings) ==="
export PREMIUM_TOKEN="$(SUBSCRIPTION_LEVEL=trial "${SCRIPT_DIR}/mint_premium_companion_jwt.sh")"
"${SCRIPT_DIR}/prewarm_companion_tts_cache.sh" "${BASE}" ru

echo ""
echo "=== VOICE-PREM-04 + 03 COMPLETE ==="
