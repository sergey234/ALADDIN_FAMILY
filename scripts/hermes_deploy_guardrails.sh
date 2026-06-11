#!/usr/bin/env bash
# Guardrails перед deploy Hermes harness (ADR-HERMES-HARNESS-PLAN §Guardrails).
set -euo pipefail

ROOT="${ROOT:-/opt/aladdin-backend}"
FAIL=0

warn() { echo "WARN: $*"; }
fail() { echo "FAIL: $*"; FAIL=1; }
ok() { echo "OK: $*"; }

echo "=== Hermes harness guardrails ==="

# 1. No v4-pro as default
if grep -q 'deepseek-v4-pro' /root/.hermes/config.yaml 2>/dev/null; then
  if grep 'default:.*deepseek-v4-pro' /root/.hermes/config.yaml 2>/dev/null; then
    fail "Hermes default model is v4-pro (402 risk)"
  else
    warn "v4-pro mentioned in config (not default)"
  fi
else
  ok "no v4-pro default in hermes config"
fi

# 2. Self-improve cron empty
CRON_DIR="/root/.hermes/cron"
if [[ -d "$CRON_DIR" ]] && [[ -n "$(ls -A "$CRON_DIR" 2>/dev/null)" ]]; then
  fail "Hermes cron dir not empty: $CRON_DIR"
else
  ok "hermes cron empty/disabled"
fi

# 3. Direct fallback enabled
if grep -qE '^FEATURE_OPENROUTER_DIRECT_FALLBACK=(1|true|yes|on)' "${ROOT}/.env" 2>/dev/null; then
  ok "FEATURE_OPENROUTER_DIRECT_FALLBACK on"
else
  warn "FEATURE_OPENROUTER_DIRECT_FALLBACK not explicitly on in ${ROOT}/.env"
fi

# 4. OpenRouter key present (not printing value)
if grep -qE '^OPENROUTER_API_KEY=sk-' "${ROOT}/.env" /root/.hermes/.env 2>/dev/null; then
  ok "OPENROUTER_API_KEY set"
else
  fail "OPENROUTER_API_KEY missing"
fi

# 5. py_compile key modules
for f in \
  "${ROOT}/security/services/llm_providers/openrouter_direct_client.py" \
  "${ROOT}/security/services/companion_llm_metrics.py" \
  "${ROOT}/security/api/routers/ai_assistant_router.py" \
  "${ROOT}/security/api/routers/ai_companion_router.py"
do
  if [[ -f "$f" ]]; then
    python3 -m py_compile "$f" && ok "compile $(basename "$f")"
  else
    warn "missing $f"
  fi
done

# 6. Health
if curl -sS -m 8 "http://127.0.0.1:8002/api/health" | grep -q '"status"'; then
  ok "api health"
else
  fail "api health"
fi

if [[ "$FAIL" -eq 0 ]]; then
  echo "=== GUARDRAILS PASS ==="
  exit 0
fi
echo "=== GUARDRAILS FAIL ==="
exit 1
