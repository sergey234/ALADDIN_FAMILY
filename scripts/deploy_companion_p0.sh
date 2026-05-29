#!/usr/bin/env bash
# Companion P0 — точечный выкат на ALADDIN backend (:8002)
# См. ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md
#
# Usage:
#   chmod +x scripts/deploy_companion_p0.sh
#   ./scripts/deploy_companion_p0.sh [ssh_user] [host] [ssh_key_path]
#
# Example:
#   ./scripts/deploy_companion_p0.sh root 149.154.65.180 ~/.ssh/aladdin_server
#
# НЕ деплоить в /opt/aladdin-telegram-shop-bot — только /opt/aladdin-backend

set -euo pipefail

SSH_USER="${1:-root}"
HOST="${2:-149.154.65.180}"
SSH_KEY="${3:-${SSH_KEY_PATH:-}}"
REMOTE_ROOT="/opt/aladdin-backend"
SERVICE="aladdin-backend.service"
TS="$(date +%Y%m%d_%H%M%S)"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

SSH_OPTS=(-o BatchMode=yes -o StrictHostKeyChecking=no)
SCP_OPTS=(-o BatchMode=yes -o StrictHostKeyChecking=no)
if [[ -n "${SSH_KEY}" ]]; then
  SSH_OPTS+=(-i "${SSH_KEY}")
  SCP_OPTS+=(-i "${SSH_KEY}")
fi

ssh_r() { ssh "${SSH_OPTS[@]}" "${SSH_USER}@${HOST}" "$@"; }
scp_f() { scp "${SCP_OPTS[@]}" "$1" "${SSH_USER}@${HOST}:$2"; }

echo ">>> Companion P0 deploy → ${SSH_USER}@${HOST}:${REMOTE_ROOT}"

FILES=(
  "main.py"
  "app/routers/auth_router.py"
  "security/api/routers/ai_companion_router.py"
  "security/api/routers/ai_platform_router.py"
  "security/api/routers/ai_voice_ws_router.py"
  "security/services/ai_platform/companion_voice_turn.py"
  "security/services/ai_platform/companion_usage.py"
  "security/api/routers/ai_assistant_router.py"
  "security/services/ai_sfm_http_chat.py"
  "security/services/hermes_client.py"
  "security/services/hermes_key_rotator.py"
  "security/services/ai_platform/jwt_claims.py"
  "security/services/ai_platform/age_policy.py"
  "security/services/ai_platform/companion_store.py"
  "security/services/ai_platform/companion_persona.py"
  "security/services/ai_platform/companion_intent_router.py"
  "security/services/ai_platform/companion_emotions.py"
  "security/services/ai_platform/companion_analytics.py"
  "security/services/ai_platform/companion_ethics.py"
  "security/services/ai_platform/companion_characters.py"
  "security/services/ai_platform/companion_mood_classifier.py"
  "security/services/ai_platform/companion_post_llm_moderation.py"
  "security/services/ai_platform/companion_stream_redis.py"
  "security/services/ai_platform/companion_life_domains.py"
  "security/services/ai_platform/companion_teen_playbook.py"
  "security/services/ai_platform/companion_social_bridge.py"
  "security/services/ai_platform/companion_trust_decay.py"
  "security/services/ai_platform/companion_family_context.py"
  "security/services/ai_platform/companion_web_search.py"
  "security/services/ai_platform/companion_attachments.py"
  "security/services/ai_platform/companion_responses_tools.py"
  "security/services/ai_platform/companion_cogs.py"
  "security/services/ai_platform/companion_workspaces.py"
  "security/services/ai_platform/companion_long_context.py"
  "security/services/ai_platform/companion_media_gen.py"
  "security/services/ai_platform/consent_resolver.py"
  "security/services/ai_platform/usage_meters.py"
  "security/services/ai_platform/policy_engine.py"
  "security/services/ai_platform/capabilities.py"
  "security/services/ai_platform/config.py"
  "security/services/ai_platform/feature_flags.py"
  "security/services/ai_platform/companion_neuro_tts.py"
  "security/services/ai_platform/companion_tts_greetings.py"
  "security/services/ai_platform/modules/companion_neuro_tts.py"
  "security/services/ai_platform/orchestrator.py"
  "security/services/ai_platform/modules/base.py"
  "security/services/ai_platform/modules/registry.py"
  "security/services/ai_platform/modules/companion.py"
  "security/services/ai_platform/modules/workspaces.py"
  "security/services/ai_platform/modules/media_gen.py"
  "security/services/ai_platform/modules/voice_realtime.py"
  "security/services/ai_platform/modules/chat_core.py"
  "security/services/ai_platform/modules/web_search.py"
)

echo ">>> [1/5] Backup on server"
ssh_r "set -e
  cd ${REMOTE_ROOT}
  mkdir -p backups/companion_p0_${TS}
  for f in ${FILES[*]}; do
    [ -f \"\$f\" ] && cp -a \"\$f\" \"backups/companion_p0_${TS}/\" || true
  done
  mkdir -p data logs
"

echo ">>> [2/5] scp files (full remote paths)"
for rel in "${FILES[@]}"; do
  local_path="${LOCAL_ROOT}/${rel}"
  if [[ ! -f "${local_path}" ]]; then
    echo "MISSING local: ${rel}" >&2
    exit 1
  fi
  remote_path="${REMOTE_ROOT}/${rel}"
  ssh_r "mkdir -p \"\$(dirname '${remote_path}')\""
  scp_f "${local_path}" "${remote_path}"
  echo "  OK ${rel}"
done

echo ">>> [3/5] Env snippet + py_compile"
ssh_r "set -e
  cd ${REMOTE_ROOT}
  grep -q COMPANION_DB_PATH .env 2>/dev/null || cat >> .env <<'EOF'

# Companion P0 (${TS})
FEATURE_VOICE_ENABLED=true
FEATURE_COMPANION_ENABLED=true
COMPANION_DB_PATH=/opt/aladdin-backend/data/companion_platform.db
EOF
  ./venv/bin/python3 -m py_compile main.py
  ./venv/bin/python3 -m py_compile app/routers/auth_router.py
  ./venv/bin/python3 -m py_compile security/api/routers/ai_companion_router.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/companion_persona.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/companion_intent_router.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/companion_emotions.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/companion_analytics.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/companion_ethics.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/companion_mood_classifier.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/companion_post_llm_moderation.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/companion_stream_redis.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/companion_life_domains.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/companion_teen_playbook.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/companion_social_bridge.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/companion_trust_decay.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/companion_family_context.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/companion_web_search.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/companion_attachments.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/companion_responses_tools.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/companion_cogs.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/companion_workspaces.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/companion_long_context.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/companion_media_gen.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/modules/workspaces.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/modules/media_gen.py
  ./venv/bin/python3 -m py_compile security/api/routers/ai_voice_ws_router.py
  ./venv/bin/python3 -m py_compile security/api/routers/ai_assistant_router.py
  ./venv/bin/python3 -m py_compile security/services/ai_sfm_http_chat.py
  ./venv/bin/python3 -m py_compile security/services/hermes_key_rotator.py
  ./venv/bin/python3 -m py_compile security/services/hermes_client.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/jwt_claims.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/companion_neuro_tts.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/companion_tts_greetings.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/modules/companion_neuro_tts.py
  grep -q FEATURE_NEURO_TTS_ENABLED .env 2>/dev/null || cat >> .env <<'EOF'

# Premium neuro-TTS (off until ELEVENLABS_* set — see docs/COMPANION_NEURO_TTS_ENV.md)
# FEATURE_NEURO_TTS_ENABLED=1
# ELEVENLABS_API_KEY=
# ELEVENLABS_VOICE_GENIE=
EOF
"

echo ">>> [4/5] Restart ${SERVICE}"
ssh_r "systemctl restart ${SERVICE} && sleep 4 && systemctl is-active ${SERVICE}"

echo ">>> [5a/5] Hermes key rotator watchdog"
if [[ -f "${LOCAL_ROOT}/scripts/hermes_llm_watchdog.sh" ]]; then
  ssh_r "mkdir -p ${REMOTE_ROOT}/scripts /var/log/aladdin-backend ${REMOTE_ROOT}/data"
  scp_f "${LOCAL_ROOT}/scripts/hermes_llm_watchdog.sh" "${REMOTE_ROOT}/scripts/hermes_llm_watchdog.sh"
  scp_f "${LOCAL_ROOT}/scripts/hermes_llm_watchdog.cron.example" "${REMOTE_ROOT}/scripts/hermes_llm_watchdog.cron.example"
  ssh_r "chmod +x ${REMOTE_ROOT}/scripts/hermes_llm_watchdog.sh"
  grep -q 'HERMES_OPENROUTER_API_KEYS' .env 2>/dev/null || cat >> .env <<'EOF'

# Hermes OpenRouter rotator (comma-separated keys; or use HERMES_OPENROUTER_KEYS_FILE)
# HERMES_OPENROUTER_API_KEYS=sk-or-v1-aaa,sk-or-v1-bbb
# HERMES_WATCHDOG_SMOKE=0
EOF
  echo "  OK hermes_llm_watchdog.sh (install cron from scripts/hermes_llm_watchdog.cron.example)"
fi

echo ">>> [5b/5] OPS-04 cost alert script"
if [[ -f "${LOCAL_ROOT}/scripts/companion_llm_cost_alert.sh" ]]; then
  ssh_r "mkdir -p ${REMOTE_ROOT}/scripts /var/log/aladdin-backend"
  scp_f "${LOCAL_ROOT}/scripts/companion_llm_cost_alert.sh" "${REMOTE_ROOT}/scripts/companion_llm_cost_alert.sh"
  ssh_r "chmod +x ${REMOTE_ROOT}/scripts/companion_llm_cost_alert.sh"
  echo "  OK companion_llm_cost_alert.sh (cron: see COMPANION_DEPLOY_P0.md)"
fi

echo ">>> [5/5] Smoke on server (localhost:8002)"
ssh_r "curl -sS -m 8 http://127.0.0.1:8002/api/health; echo"
ssh_r "curl -sS -m 12 http://127.0.0.1:8002/openapi.json -o /tmp/openapi_companion.json && python3 - <<'PY'
import json
j=json.load(open('/tmp/openapi_companion.json'))
want=[
 '/api/ai/companion/characters',
 '/api/ai/companion/chat',
 '/api/ai/companion/capabilities',
 '/api/ai/companion/analytics',
 '/api/ai/voice/ephemeral-token',
]
for p in want:
    m=j.get('paths',{}).get(p,{})
    print(p, sorted(m.keys()) if m else 'MISSING')
PY"
ssh_r "curl -sS -m 5 -o /dev/null -w 'voice_ws_backend=%{http_code}\n' -H 'Connection: Upgrade' -H 'Upgrade: websocket' -H 'Sec-WebSocket-Version: 13' -H 'Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==' 'http://127.0.0.1:8002/api/ai/voice/realtime?token=INVALID'"

echo ""
echo ">>> Done. External check (from your Mac):"
echo "  ./scripts/verify_companion_p0_prod.sh https://aladdin-ai.ru"
echo ""
echo "nginx: для WebSocket голоса нужен Upgrade на /api/ai/voice/realtime (см. docs/COMPANION_DEPLOY_P0.md)"
