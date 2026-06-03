#!/usr/bin/env bash
# hero-x-61 — deploy companion hero enhancements (phases 1–5) + wellness batch4 router sync
# Usage: ./scripts/deploy_hero_x_phase6.sh [user] [host] [ssh_key]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
USER="${1:-root}"
HOST="${2:-149.154.65.180}"
KEY="${3:-${SSH_KEY_PATH:-$HOME/.ssh/aladdin_server}}"

echo ">>> hero-x-61 deploy: companion_p0 + hero modules → ${USER}@${HOST}"

# Extend companion P0 with hero-x backend files (rsync knowledge dirs on server)
"${SCRIPT_DIR}/deploy_companion_p0.sh" "${USER}" "${HOST}" "${KEY}"

SSH_OPTS=(-o BatchMode=yes -o StrictHostKeyChecking=no)
[[ -n "${KEY}" && -f "${KEY}" ]] && SSH_OPTS+=(-i "${KEY}")
LOCAL_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
REMOTE="/opt/aladdin-backend"

echo ">>> hero-x knowledge packs + new modules"
ssh "${SSH_OPTS[@]}" "${USER}@${HOST}" "mkdir -p ${REMOTE}/security/services/ai_platform/companion_knowledge"
scp_r() { scp -r "${SSH_OPTS[@]}" "$1" "${USER}@${HOST}:$2"; }

for sub in humor vedic psychology empathy; do
  scp_r "${LOCAL_ROOT}/security/services/ai_platform/companion_knowledge/${sub}" \
    "${REMOTE}/security/services/ai_platform/companion_knowledge/"
  echo "  OK companion_knowledge/${sub}/"
done

HERO_FILES=(
  security/services/ai_platform/companion_humor_policy.py
  security/services/ai_platform/companion_experiment.py
  security/services/ai_platform/companion_wisdom.py
  security/services/ai_platform/companion_psychology.py
  security/services/ai_platform/companion_pattern_reflect.py
  security/services/ai_platform/companion_empathy.py
  security/services/ai_platform/companion_topic_policy.py
  security/services/ai_platform/companion_response_guard.py
  security/services/ai_platform/companion_prompt_assembler.py
  security/services/ai_platform/companion_golden_scorer.py
  security/services/ai_platform/companion_intent_router.py
  security/services/ai_platform/companion_social_bridge.py
  security/services/ai_platform/consent_resolver.py
  security/services/ai_platform/feature_flags.py
  security/api/routers/ai_companion_router.py
)

for f in "${HERO_FILES[@]}"; do
  scp "${SSH_OPTS[@]}" "${LOCAL_ROOT}/${f}" "${USER}@${HOST}:${REMOTE}/${f}"
  echo "  OK ${f}"
done

echo ">>> wellness batch4 (router + packs)"
"${SCRIPT_DIR}/deploy_wellness_batch4.sh" "${USER}" "${HOST}" "${KEY}" || true

echo ">>> py_compile hero modules on server"
ssh "${SSH_OPTS[@]}" "${USER}@${HOST}" "cd ${REMOTE} && ./venv/bin/python3 -m py_compile \
  security/services/ai_platform/companion_humor_policy.py \
  security/services/ai_platform/companion_wisdom.py \
  security/services/ai_platform/companion_golden_scorer.py \
  security/api/routers/ai_companion_router.py"

echo ">>> restart + external verify"
ssh "${SSH_OPTS[@]}" "${USER}@${HOST}" "systemctl restart aladdin-backend.service && sleep 4 && systemctl is-active aladdin-backend.service"

if [[ -f "${SCRIPT_DIR}/verify_companion_p0_prod.sh" ]]; then
  "${SCRIPT_DIR}/verify_companion_p0_prod.sh" "https://aladdin-ai.ru" || echo "WARN: prod verify failed — check manually"
fi

echo ">>> hero-x-61 deploy complete $(date -u +%Y-%m-%dT%H:%M:%SZ)"
