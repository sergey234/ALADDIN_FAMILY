#!/usr/bin/env bash
# VPN32: запускать с машины ВНЕ основного VPS (cron + алерт при сбое).
set -euo pipefail

URLS="${ALADDIN_EXTERNAL_SMOKE_URLS:-https://aladdin-ai.ru/v1/legal/vpn-instructions,https://aladdin-ai.ru/v1/legal/vpn-terms,https://aladdin-ai.ru/sub/__smoke_unknown__}"
TIMEOUT="${ALADDIN_EXTERNAL_SMOKE_TIMEOUT:-12}"
# Для /sub/__smoke_unknown__ ожидаем 404, не 5xx:
SUB_SMOKE_PATH="${ALADDIN_EXTERNAL_SUB_SMOKE_PATH:-https://aladdin-ai.ru/sub/__smoke_unknown__}"
TELEGRAM_TOKEN="${ALERT_TELEGRAM_BOT_TOKEN:-${ALADDIN_ALERT_TELEGRAM_BOT_TOKEN:-}}"
TELEGRAM_CHAT="${ALERT_TELEGRAM_CHAT_ID:-${ALADDIN_ALERT_TELEGRAM_CHAT_ID:-}}"
FAIL=0
MSG=""

notify_telegram() {
  local text="$1"
  [[ -z "$TELEGRAM_TOKEN" || -z "$TELEGRAM_CHAT" ]] && return 0
  curl -fsS -m 10 -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/sendMessage" \
    -d "chat_id=${TELEGRAM_CHAT}" \
    --data-urlencode "text=${text}" >/dev/null 2>&1 || true
}

check_url() {
  local u="$1"
  local code
  code=$(curl -sS -m "$TIMEOUT" -o /dev/null -w '%{http_code}' "$u" || echo "000")
  if [[ "$code" =~ ^2 ]]; then
    echo "OK: $u ($code)"
    return 0
  fi
  echo "FAIL: $u (HTTP $code)" >&2
  MSG="${MSG}\nFAIL $u HTTP $code"
  return 1
}

check_sub_smoke() {
  local code
  code=$(curl -sS -m "$TIMEOUT" -o /dev/null -w '%{http_code}' "$SUB_SMOKE_PATH" || echo "000")
  if [[ "$code" == "404" ]]; then
    echo "OK: $SUB_SMOKE_PATH (404 expected)"
    return 0
  fi
  echo "FAIL: $SUB_SMOKE_PATH (expected 404, got $code)" >&2
  MSG="${MSG}\nFAIL sub smoke HTTP $code"
  return 1
}

IFS=',' read -r -a arr <<< "$URLS"
for u in "${arr[@]}"; do
  u="${u#"${u%%[![:space:]]*}"}"
  u="${u%"${u##*[![:space:]]}"}"
  [[ -z "$u" ]] && continue
  [[ "$u" == *"/sub/"* ]] && continue
  check_url "$u" || FAIL=1
done

check_sub_smoke || FAIL=1

if [[ "$FAIL" -ne 0 ]]; then
  notify_telegram "ALADDIN VPN external smoke FAILED:${MSG}"
  exit 1
fi

echo "external_vpn_smoke: all OK"
exit 0
