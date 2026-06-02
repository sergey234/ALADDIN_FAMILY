#!/usr/bin/env bash
# Wellness Phase 1 — выкат на ALADDIN backend (:8002)
# См. ALADDIN_SERVER_CONNECTION_GUIDE_FOR_ML_SYSTEMS.md §10

set -euo pipefail

SSH_USER="${1:-root}"
HOST="${2:-149.154.65.180}"
SSH_KEY="${3:-${SSH_KEY_PATH:-}}"
REMOTE_ROOT="/opt/aladdin-backend"
SERVICE="aladdin-backend.service"
TS="$(date +%Y%m%d_%H%M%S)"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

SSH_OPTS=(-o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15)
SCP_OPTS=(-o BatchMode=yes -o StrictHostKeyChecking=no -o ConnectTimeout=15)
if [[ -n "${SSH_KEY}" ]]; then
  SSH_OPTS+=(-i "${SSH_KEY}")
  SCP_OPTS+=(-i "${SSH_KEY}")
fi

ssh_r() { ssh "${SSH_OPTS[@]}" "${SSH_USER}@${HOST}" "$@"; }
scp_f() { scp "${SCP_OPTS[@]}" "$1" "${SSH_USER}@${HOST}:$2"; }
scp_r() { scp -r "${SCP_OPTS[@]}" "$1" "${SSH_USER}@${HOST}:$2"; }

echo ">>> Wellness P1 deploy → ${SSH_USER}@${HOST}:${REMOTE_ROOT}"

FILES=(
  "main.py"
  "security/api/routers/wellness_router.py"
  "security/api/routers/ai_companion_router.py"
  "security/services/ai_platform/companion_intent_router.py"
  "security/services/ai_platform/feature_flags.py"
  "security/services/ai_platform/companion_store.py"
  "security/services/ai_platform/wellness_four_pillars.py"
  "security/services/ai_platform/wellness_pillar_guard.py"
  "security/services/ai_platform/wellness_escalation.py"
  "security/services/ai_platform/wellness_referral.py"
  "security/services/ai_platform/wellness_prompt_builder.py"
  "security/services/ai_platform/wellness_pillar_prompt_util.py"
  "security/services/ai_platform/wellness_cognitive_prompt.py"
  "security/services/ai_platform/wellness_humanistic_prompt.py"
  "security/services/ai_platform/wellness_jung_prompt.py"
  "security/services/ai_platform/wellness_journal.py"
  "security/services/ai_platform/wellness_assessments.py"
  "security/services/ai_platform/wellness_i18n_loader.py"
  "security/services/ai_platform/wellness_age_policy.py"
  "security/services/ai_platform/wellness_triggers.py"
  "security/services/ai_platform/wellness_orchestrator.py"
  "security/services/ai_platform/wellness_crisis_monitor.py"
  "security/services/ai_platform/companion_ethics.py"
  "security/services/ai_platform/wellness_pack_registry.py"
  "security/services/ai_platform/wellness_agent_hints.py"
  "security/services/ai_platform/wellness_gdpr.py"
  "security/services/ai_platform/wellness_pillar_session.py"
  "security/services/ai_platform/wellness_cbt_exercises.py"
  "security/services/ai_platform/wellness_behavioral_exercises.py"
  "security/services/ai_platform/wellness_jung_exercises.py"
  "security/services/ai_platform/wellness_outcomes.py"
  "security/services/ai_platform/wellness_session_recap.py"
  "security/services/ai_platform/wellness_insights.py"
  "security/services/ai_platform/wellness_pillar_session.py"
  "security/services/ai_platform/wellness_outcome_followup.py"
  "security/services/ai_platform/wellness_pillar_fatigue.py"
  "security/services/ai_platform/wellness_habit_plans.py"
  "security/services/ai_platform/wellness_insights_extractor.py"
  "security/services/ai_platform/wellness_emotion_agent.py"
  "security/services/ai_platform/wellness_plan_agent.py"
  "security/services/ai_platform/wellness_mood_routing.py"
  "security/services/ai_platform/wellness_trauma_referral.py"
  "security/services/ai_platform/wellness_alliance.py"
  "security/services/ai_platform/wellness_hub_ab.py"
  "security/services/ai_platform/wellness_weekly_meaning.py"
  "security/services/ai_platform/wellness_family_themes.py"
  "security/services/ai_platform/wellness_security_fusion.py"
  "security/services/ai_platform/wellness_streaks.py"
  "security/services/ai_platform/wellness_clinician_export.py"
  "security/services/ai_platform/wellness_parent_playbook.py"
  "security/services/ai_platform/wellness_api_errors.py"
  "security/services/ai_platform/wellness_premium_access.py"
  "security/services/ai_platform/wellness_values_card.py"
  "security/services/ai_platform/wellness_elderly_journal.py"
  "security/services/ai_platform/wellness_pillar_rive.py"
  "security/services/ai_platform/wellness_family_prompt.py"
  "security/services/ai_platform/wellness_seasonal.py"
  "security/services/ai_platform/wellness_voice_senior.py"
  "security/services/ai_platform/wellness_sleep_stories.py"
  "security/services/ai_platform/wellness_store_postgres.py"
  "security/services/ai_platform/wellness_store_dual.py"
  "security/services/ai_platform/wellness_canary.py"
  "security/services/ai_platform/wellness_pg_schema.sql"
  "scripts/migrate_wellness_sqlite_to_pg.py"
  "security/services/ai_platform/wellness_exercise_engine.py"
  "security/services/ai_platform/wellness_together_mode.py"
  "security/services/ai_platform/wellness_reflective_modes.py"
  "security/services/ai_platform/wellness_reflective_guards.py"
  "security/services/ai_platform/wellness_reflective_prompt.py"
  "security/services/ai_platform/wellness_alerts.py"
  "security/services/ai_platform/wellness_scheduler.py"
  "security/services/ai_platform/wellness_analytics.py"
  "security/services/ai_platform/wellness_nudge.py"
  "Tests/test_wellness_phase1.py"
  "Tests/test_wellness_phase2.py"
  "Tests/test_wellness_gates.py"
  "Tests/test_wellness_alerts.py"
  "Tests/test_wellness_nudge.py"
  "Tests/test_wellness_pillar_prompts.py"
  "Tests/test_wellness_session_flow.py"
  "Tests/test_wellness_fatigue_habits.py"
  "Tests/test_wellness_agents.py"
  "Tests/test_wellness_trauma_alliance.py"
  "Tests/test_wellness_phase2_final.py"
  "Tests/test_wellness_i18n.py"
  "Tests/test_wellness_exercises_i18n.py"
  "Tests/test_wellness_export_i18n.py"
  "Tests/test_wellness_push_i18n.py"
  "Tests/test_wellness_age_i18n.py"
  "Tests/test_wellness_errors_i18n.py"
  "Tests/test_wellness_phase3.py"
  "Tests/test_wellness_canary_pg.py"
  "scripts/check_wellness_l10n.py"
)

DIRS=(
  "security/services/ai_platform/wellness_knowledge"
  "security/services/ai_platform/wellness_i18n"
)

echo ">>> [0/5] External health"
curl -sS -m 8 "http://${HOST}:8002/api/health" || true
echo ""

echo ">>> [1/5] Backup on server"
ssh_r "set -e
  cd ${REMOTE_ROOT}
  mkdir -p backups/wellness_p1_${TS}
  for f in ${FILES[*]}; do
    [ -f \"\$f\" ] && cp -a \"\$f\" \"backups/wellness_p1_${TS}/\" || true
  done
  mkdir -p data logs
"

echo ">>> [2/5] scp files"
for rel in "${FILES[@]}"; do
  local_path="${LOCAL_ROOT}/${rel}"
  [[ -f "${local_path}" ]] || { echo "MISSING ${rel}" >&2; exit 1; }
  remote_path="${REMOTE_ROOT}/${rel}"
  ssh_r "mkdir -p \"\$(dirname '${remote_path}')\""
  scp_f "${local_path}" "${remote_path}"
  echo "  OK ${rel}"
done

for rel in "${DIRS[@]}"; do
  local_path="${LOCAL_ROOT}/${rel}"
  [[ -d "${local_path}" ]] || { echo "MISSING dir ${rel}" >&2; exit 1; }
  remote_path="${REMOTE_ROOT}/${rel}"
  ssh_r "mkdir -p \"${remote_path}\""
  # Copy directory *contents* (avoid wellness_i18n/wellness_i18n nesting on re-deploy)
  scp -r "${SCP_OPTS[@]}" "${local_path}/." "${SSH_USER}@${HOST}:${remote_path}/"
  echo "  OK ${rel}/"
done
# Ensure nested packs (humanistic/behavioral/…) land on server
for sub in cognitive humanistic behavioral jung; do
  if [[ -d "${LOCAL_ROOT}/security/services/ai_platform/wellness_knowledge/${sub}" ]]; then
    ssh_r "mkdir -p ${REMOTE_ROOT}/security/services/ai_platform/wellness_knowledge/${sub}"
    scp_r "${LOCAL_ROOT}/security/services/ai_platform/wellness_knowledge/${sub}" \
      "${REMOTE_ROOT}/security/services/ai_platform/wellness_knowledge/"
    echo "  OK wellness_knowledge/${sub}/"
  fi
done

echo ">>> [3/5] .env + py_compile"
ssh_r "set -e
  cd ${REMOTE_ROOT}
  touch .env
  for kv in FEATURE_WELLNESS_ENABLED=1 FEATURE_WELLNESS_ORCHESTRATOR=1 FEATURE_WELLNESS_REFLECTIVE=1 FEATURE_WELLNESS_JUNG=1 WELLNESS_CANARY_PERCENT=100 FEATURE_WELLNESS_PARENT_LLM=0 WELLNESS_PG_DUAL_WRITE=0 WELLNESS_PG_READ=0; do
    key=\${kv%%=*}
    if grep -q \"^\${key}=\" .env 2>/dev/null; then
      sed -i.bak \"s|^\${key}=.*|\${kv}|\" .env
    else
      echo \"\${kv}\" >> .env
    fi
  done
  ./venv/bin/python3 -m py_compile main.py
  ./venv/bin/python3 -m py_compile security/api/routers/wellness_router.py
  ./venv/bin/python3 -m py_compile security/api/routers/ai_companion_router.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/feature_flags.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/companion_store.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_four_pillars.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_pillar_guard.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_escalation.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_referral.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_prompt_builder.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_journal.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_assessments.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_exercise_engine.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_i18n_loader.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_age_policy.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_triggers.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/companion_intent_router.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_orchestrator.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_crisis_monitor.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_pack_registry.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_agent_hints.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_gdpr.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_pillar_session.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_exercise_engine.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_outcomes.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_session_recap.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_api_errors.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_premium_access.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_values_card.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_elderly_journal.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_pillar_rive.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_family_prompt.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_seasonal.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_voice_senior.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_sleep_stories.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_store_postgres.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_store_dual.py
  ./venv/bin/python3 -m py_compile security/services/ai_platform/wellness_canary.py
  PYTHONPATH=. ./venv/bin/python3 -m pytest Tests/test_wellness_phase1.py Tests/test_wellness_phase2.py Tests/test_wellness_phase3.py Tests/test_wellness_errors_i18n.py -q --tb=short 2>/dev/null || true
"

echo ">>> [4/5] Restart ${SERVICE}"
ssh_r "systemctl restart ${SERVICE} && sleep 5 && systemctl is-active ${SERVICE}"

echo ">>> [5/6] OpenAPI paths"
ssh_r "curl -sS -m 8 http://127.0.0.1:8002/api/health; echo"
ssh_r "curl -sS -m 12 http://127.0.0.1:8002/openapi.json -o /tmp/openapi_wellness.json && python3 - <<'PY'
import json
j=json.load(open('/tmp/openapi_wellness.json'))
paths=j.get('paths',{})
want=[
 '/api/wellness/pillars',
 '/api/wellness/consent',
 '/api/wellness/checkin',
 '/api/wellness/journal',
 '/api/wellness/triggers/status',
 '/api/wellness/assessments/phq-lite/schema',
 '/api/wellness/assessments/phq-lite/submit',
 '/api/wellness/session/pillar',
 '/api/wellness/escalation/level',
 '/api/wellness/settings',
 '/api/wellness/settings/parent-share',
 '/api/wellness/referral',
 '/api/wellness/session/suggest-pillar',
 '/api/wellness/session/loop',
 '/api/wellness/crisis/status',
 '/api/wellness/premium/eligibility',
 '/api/wellness/export/personal',
 '/api/wellness/data',
 '/api/wellness/session/recap',
 '/api/wellness/exercises/catalog',
 '/api/wellness/exercises/start',
 '/api/wellness/timeline',
 '/api/wellness/outcomes',
 '/api/wellness/assessments/phq-9/schema',
 '/api/wellness/assessments/phq-9/submit',
 '/api/wellness/assessments/gad-7/schema',
 '/api/wellness/assessments/gad-7/submit',
 '/api/wellness/errors/catalog',
 '/api/wellness/seasonal/playbooks',
 '/api/wellness/sleep/stories',
 '/api/wellness/pillar/rive',
 '/api/wellness/humanistic/values-card',
 '/api/wellness/family/talk-prompts',
 '/api/wellness/export/pdf-labels',
 '/api/wellness/widget/copy',
 '/api/wellness/store/backend',
 '/api/wellness/canary/status',
]
for p in want:
    m=paths.get(p,{})
    print(p, sorted(m.keys()) if m else 'MISSING')
PY"

echo ">>> [6/6] Auth smoke (JWT + all wellness endpoints)"
scp_f "${LOCAL_ROOT}/scripts/vps_smoke_wellness.py" "${REMOTE_ROOT}/scripts/vps_smoke_wellness.py"
ssh_r "chmod +x ${REMOTE_ROOT}/scripts/vps_smoke_wellness.py && cd ${REMOTE_ROOT} && PYTHONPATH=${REMOTE_ROOT} ./venv/bin/python3 scripts/vps_smoke_wellness.py"

echo ""
echo ">>> Done."
echo "  VPS localhost smoke:  cd ${REMOTE_ROOT} && python3 scripts/vps_smoke_wellness.py"
echo "  Prod via nginx (как iOS):  ./scripts/verify_wellness_prod.sh https://aladdin-ai.ru"
echo "  Прямой IP :8002 снаружи часто закрыт — используйте https://aladdin-ai.ru"
