#!/usr/bin/env bash
# Настройка neuro-TTS на VPS (секреты НЕ в git).
#
# Порядок PO: VOICE-PREM-04 (3 voice id) → VOICE-PREM-03 (пилот genie + prewarm).
#
# Локально (перед вызовом) — все три id обязательны:
#   export ELEVENLABS_API_KEY="sk_..."
#   export ELEVENLABS_VOICE_UNICORN="<uuid>"
#   export ELEVENLABS_VOICE_GENIE="<uuid>"
#   export ELEVENLABS_VOICE_ALADDIN="<uuid>"
#
# Usage:
#   ./scripts/configure_companion_neuro_tts_env.sh [ssh_user] [host] [ssh_key]
#
set -euo pipefail

SSH_USER="${1:-root}"
HOST="${2:-149.154.65.180}"
SSH_KEY="${3:-${SSH_KEY_PATH:-}}"
REMOTE_ROOT="/opt/aladdin-backend"
SECRETS_FILE="${REMOTE_ROOT}/secrets/elevenlabs.env"

missing=()
[[ -z "${ELEVENLABS_API_KEY:-}" ]] && missing+=("ELEVENLABS_API_KEY")
[[ -z "${ELEVENLABS_VOICE_UNICORN:-}" ]] && missing+=("ELEVENLABS_VOICE_UNICORN")
[[ -z "${ELEVENLABS_VOICE_GENIE:-}" ]] && missing+=("ELEVENLABS_VOICE_GENIE")
[[ -z "${ELEVENLABS_VOICE_ALADDIN:-}" ]] && missing+=("ELEVENLABS_VOICE_ALADDIN")

if [[ ${#missing[@]} -gt 0 ]]; then
  echo "VOICE-PREM-04: set all of: ${missing[*]}" >&2
  echo "See docs/COMPANION_ELEVENLABS_VOICES_RU.md" >&2
  exit 1
fi

if [[ "${ELEVENLABS_VOICE_UNICORN}" == "${ELEVENLABS_VOICE_GENIE}" ]] \
  || [[ "${ELEVENLABS_VOICE_UNICORN}" == "${ELEVENLABS_VOICE_ALADDIN}" ]] \
  || [[ "${ELEVENLABS_VOICE_GENIE}" == "${ELEVENLABS_VOICE_ALADDIN}" ]]; then
  echo "VOICE-PREM-04: unicorn, genie, aladdin must use three different voice IDs." >&2
  exit 1
fi

SSH_OPTS=(-o BatchMode=yes -o StrictHostKeyChecking=no)
[[ -n "${SSH_KEY}" ]] && SSH_OPTS+=(-i "${SSH_KEY}")

ssh_r() { ssh "${SSH_OPTS[@]}" "${SSH_USER}@${HOST}" "$@"; }

ssh_r "set -e
  mkdir -p ${REMOTE_ROOT}/secrets
  chmod 700 ${REMOTE_ROOT}/secrets
  umask 077
  cat > ${SECRETS_FILE} <<EOF
ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}
ELEVENLABS_MODEL=${ELEVENLABS_MODEL:-eleven_flash_v2_5}
ELEVENLABS_VOICE_UNICORN=${ELEVENLABS_VOICE_UNICORN}
ELEVENLABS_VOICE_GENIE=${ELEVENLABS_VOICE_GENIE}
ELEVENLABS_VOICE_ALADDIN=${ELEVENLABS_VOICE_ALADDIN}
EOF
  chmod 600 ${SECRETS_FILE}
  grep -q 'secrets/elevenlabs.env' ${REMOTE_ROOT}/.env 2>/dev/null || cat >> ${REMOTE_ROOT}/.env <<'ENVEOF'

# Companion neuro-TTS (Premium) — source secrets/elevenlabs.env
set -a
[ -f /opt/aladdin-backend/secrets/elevenlabs.env ] && . /opt/aladdin-backend/secrets/elevenlabs.env
set +a
FEATURE_NEURO_TTS_ENABLED=1
COMPANION_TTS_CACHE_MAX=30
ENVEOF
  grep -q '^FEATURE_NEURO_TTS_ENABLED=' ${REMOTE_ROOT}/.env && \
    sed -i 's/^FEATURE_NEURO_TTS_ENABLED=.*/FEATURE_NEURO_TTS_ENABLED=1/' ${REMOTE_ROOT}/.env || \
    echo 'FEATURE_NEURO_TTS_ENABLED=1' >> ${REMOTE_ROOT}/.env
  systemctl restart aladdin-backend.service
  sleep 2
  systemctl is-active aladdin-backend.service
"
echo "OK: VOICE-PREM-04 — 3 hero voices on ${HOST} (${SECRETS_FILE})"
echo "Next: VOICE-PREM-03 — ./scripts/prewarm_companion_tts_cache.sh + smoke genie on Premium"
