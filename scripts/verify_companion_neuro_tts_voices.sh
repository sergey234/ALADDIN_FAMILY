#!/usr/bin/env bash
# VOICE-PREM-04: на VPS должны быть 3 разных ELEVENLABS_VOICE_* (без вывода секретов).
#
# Usage: ./scripts/verify_companion_neuro_tts_voices.sh [ssh_user] [host] [ssh_key]
#
set -euo pipefail

SSH_USER="${1:-root}"
HOST="${2:-149.154.65.180}"
SSH_KEY="${3:-${SSH_KEY_PATH:-}}"
REMOTE_ROOT="/opt/aladdin-backend"

SSH_OPTS=(-o BatchMode=yes -o StrictHostKeyChecking=no)
[[ -n "${SSH_KEY}" ]] && SSH_OPTS+=(-i "${SSH_KEY}")

ssh "${SSH_OPTS[@]}" "${SSH_USER}@${HOST}" "set -a
[ -f ${REMOTE_ROOT}/secrets/elevenlabs.env ] && . ${REMOTE_ROOT}/secrets/elevenlabs.env
set +a
cd ${REMOTE_ROOT}
./venv/bin/python3 - <<'PY'
import os
import sys

sys.path.insert(0, '.')
from security.services.ai_platform.companion_neuro_tts import (
    all_hero_voice_ids_configured,
    neuro_tts_configured,
    voice_id_for_character,
    _DEFAULT_VOICE_BY_CHARACTER,
)

key = bool(os.getenv('ELEVENLABS_API_KEY', '').strip())
heroes = {h: _DEFAULT_VOICE_BY_CHARACTER.get(h, '') for h in ('unicorn', 'genie', 'aladdin')}
missing = [h for h, v in heroes.items() if not v]
uniq = len(set(heroes.values()))
print('api_key_set=', key)
print('voices_configured=', all_hero_voice_ids_configured())
print('neuro_tts_ready=', neuro_tts_configured())
print('unique_voice_ids=', uniq, '/ 3')
if missing:
    print('missing_heroes=', ','.join(missing))
    sys.exit(1)
if uniq < 3:
    print('ERROR: voice ids must be distinct for unicorn, genie, aladdin')
    sys.exit(1)
for h in ('unicorn', 'genie', 'aladdin'):
    assert voice_id_for_character(h), h
print('VOICE-PREM-04 OK')
PY
"
