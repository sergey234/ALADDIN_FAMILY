#!/usr/bin/env bash
# Contabo: getMe health for Telegram Bot API (br-b* / smart-restart br-c*).
# Exit 0 = OK; exit 1 = FAIL.
# Rule: getMe FAIL → never systemctl restart (only alert after streak).
set -euo pipefail

ENV_FILE="${TELEGRAM_BOT_ENV_FILE:-/opt/aladdin-telegram-shop-bot/shared/.env}"
STATE_DIR="${TELEGRAM_BOT_API_STATE_DIR:-/var/lib/aladdin-bot-ops}"
LOG_FILE="${TELEGRAM_BOT_API_HEALTH_LOG:-/var/log/aladdin-telegram-bot-api-health.log}"
TIMEOUT_SEC="${TELEGRAM_BOT_API_GETME_TIMEOUT_SEC:-8}"
LATENCY_WARN_SEC="${TELEGRAM_BOT_API_LATENCY_WARN_SEC:-5}"
FAIL_STREAK_NEED="${TELEGRAM_BOT_API_FAIL_STREAK:-3}"
BOT_LOG="${TELEGRAM_BOT_LOG:-/opt/aladdin-telegram-shop-bot/logs/bot.log}"
UNIT="${TELEGRAM_BOT_SYSTEMD_UNIT:-aladdin-telegram-bot.service}"
SMART_RESTART="${TELEGRAM_BOT_SMART_RESTART_ENABLED:-false}"
MAX_RESTART_PER_HOUR="${TELEGRAM_BOT_SMART_RESTART_MAX_PER_HOUR:-3}"
MIN_SECONDS_BETWEEN="${TELEGRAM_BOT_SMART_RESTART_MIN_SECONDS:-1800}"
VPN_OPS_NOTIFY="${VPN_OPS_NOTIFY_SH:-/opt/aladdin-shop-vpn-api/deploy/scripts/vpn_ops_notify.sh}"
DRY_RUN="${TELEGRAM_BOT_API_HEALTH_DRY_RUN:-false}"

mkdir -p "$STATE_DIR" 2>/dev/null || STATE_DIR="/tmp/aladdin-bot-ops"
mkdir -p "$STATE_DIR"
touch "$LOG_FILE" 2>/dev/null || LOG_FILE="/tmp/aladdin-telegram-bot-api-health.log"

ts() { date -u +"%Y-%m-%dT%H:%M:%SZ"; }

log() {
  local line
  line="$(ts) $*"
  echo "$line" >>"$LOG_FILE" 2>/dev/null || true
  echo "$line"
}

_env_get() {
  local k="$1"
  [[ -f "$ENV_FILE" ]] || return 0
  grep -m1 "^${k}=" "$ENV_FILE" 2>/dev/null | cut -d= -f2- | tr -d '"' | tr -d "'"
}

TOK="$(_env_get BOT_TOKEN)"
if [[ -z "${TOK:-}" ]]; then
  log "ERROR no BOT_TOKEN in $ENV_FILE"
  exit 1
fi

BODY="${STATE_DIR}/getme.body"
METRICS=""
CURL_EC=0
set +e
METRICS=$(curl -4 --http1.1 -sS -m "$TIMEOUT_SEC" \
  -o "$BODY" \
  -w "%{http_code} %{time_total}" \
  "https://api.telegram.org/bot${TOK}/getMe" 2>/dev/null)
CURL_EC=$?
set -e

HTTP_CODE=$(echo "$METRICS" | awk '{print $1}')
TIME_TOTAL=$(echo "$METRICS" | awk '{print $2}')
PROBE_OK=0

if [[ "$CURL_EC" -eq 0 && "$HTTP_CODE" == "200" ]]; then
  if awk -v t="${TIME_TOTAL:-99}" -v w="$LATENCY_WARN_SEC" 'BEGIN { exit !(t+0 < w+0) }'; then
    PROBE_OK=1
  else
    log "WARN getMe slow http=$HTTP_CODE t=${TIME_TOTAL}s threshold=${LATENCY_WARN_SEC}s"
  fi
fi

STREAK_FILE="${STATE_DIR}/getme_fail_streak"
PREV_STATE_FILE="${STATE_DIR}/getme_last_state"
STREAK=0
[[ -f "$STREAK_FILE" ]] && STREAK=$(cat "$STREAK_FILE" 2>/dev/null || echo 0)
PREV_STATE="unknown"
[[ -f "$PREV_STATE_FILE" ]] && PREV_STATE=$(cat "$PREV_STATE_FILE" 2>/dev/null || echo unknown)

alert_ops() {
  local key="$1"
  local msg="$2"
  if [[ "$DRY_RUN" == "true" || "$DRY_RUN" == "1" ]]; then
    log "DRY_RUN alert key=$key msg=$msg"
    echo "$msg" >"${STATE_DIR}/last_alert.txt"
    return 0
  fi
  if [[ -f "$VPN_OPS_NOTIFY" ]]; then
    # shellcheck disable=SC1090
    source "$VPN_OPS_NOTIFY"
    vpn_ops_alert "$key" "$msg" || true
  else
    log "WARN no vpn_ops_notify at $VPN_OPS_NOTIFY — alert skipped: $msg"
  fi
}

if [[ "$PROBE_OK" -eq 1 ]]; then
  echo 0 >"$STREAK_FILE"
  echo ok >"$PREV_STATE_FILE"
  log "OK getMe=200 t=${TIME_TOTAL}s"
  if [[ "$PREV_STATE" == "fail" ]]; then
    alert_ops "telegram_bot_api:recovered" "✅ Telegram Bot API getMe RECOVERED on Contabo (t=${TIME_TOTAL}s)"
  fi
else
  STREAK=$((STREAK + 1))
  echo "$STREAK" >"$STREAK_FILE"
  echo fail >"$PREV_STATE_FILE"
  log "FAIL getMe http=${HTTP_CODE:-0} curl_ec=$CURL_EC t=${TIME_TOTAL:-?} streak=$STREAK"
  if [[ "$STREAK" -ge "$FAIL_STREAK_NEED" ]]; then
    alert_ops "telegram_bot_api:fail" \
      "❌ Telegram Bot API getMe FAILED on Contabo (бот может не видеть /start). http=${HTTP_CODE:-0} t=${TIME_TOTAL:-?} streak=$STREAK"
  fi
fi

maybe_smart_restart() {
  [[ "$SMART_RESTART" == "true" || "$SMART_RESTART" == "1" ]] || return 0
  if [[ "$PROBE_OK" -ne 1 ]]; then
    log "smart-restart SKIP (getMe FAIL — never restart)"
    return 0
  fi
  local active
  active=$(systemctl is-active "$UNIT" 2>/dev/null || echo inactive)
  [[ "$active" == "active" ]] || {
    log "smart-restart SKIP unit=$active"
    return 0
  }
  [[ -f "$BOT_LOG" ]] || {
    log "smart-restart SKIP no bot log"
    return 0
  }
  local tail80
  tail80=$(tail -n 80 "$BOT_LOG" 2>/dev/null || true)
  if echo "$tail80" | grep -q "Update id="; then
    log "smart-restart SKIP (recent Update id= in log)"
    return 0
  fi
  if ! echo "$tail80" | grep -qE "TelegramNetworkError|Request timeout|HTTP Client says - Request timeout"; then
    log "smart-restart SKIP (no timeout storm evidence)"
    return 0
  fi

  local count_file="${STATE_DIR}/smart_restart.count"
  local last_file="${STATE_DIR}/smart_restart.last_ts"
  local now_h count stored_h stored_c
  now_h=$(date -u +"%Y%m%d%H")
  if [[ -f "$last_file" ]]; then
    local last_ts now_ts age
    last_ts=$(cat "$last_file" 2>/dev/null || echo 0)
    now_ts=$(date +%s)
    age=$((now_ts - last_ts))
    if [[ "$age" -lt "$MIN_SECONDS_BETWEEN" ]]; then
      log "smart-restart SKIP (cooldown age=${age}s need=${MIN_SECONDS_BETWEEN}s)"
      return 0
    fi
  fi
  count=0
  if [[ -f "$count_file" ]]; then
    stored_h=$(awk '{print $1}' "$count_file")
    stored_c=$(awk '{print $2}' "$count_file")
    if [[ "$stored_h" == "$now_h" ]]; then
      count=${stored_c:-0}
    fi
  fi
  if [[ "$count" -ge "$MAX_RESTART_PER_HOUR" ]]; then
    alert_ops "telegram_bot_api:restart_storm" \
      "🚨 smart-restart limit ${MAX_RESTART_PER_HOUR}/hour reached — нужны руки / возможен долгий outage"
    log "smart-restart BLOCKED storm guard count=$count"
    return 0
  fi
  count=$((count + 1))
  echo "$now_h $count" >"$count_file"
  date +%s >"$last_file"
  if [[ "$DRY_RUN" == "true" || "$DRY_RUN" == "1" ]]; then
    log "DRY_RUN would systemctl restart $UNIT"
    alert_ops "telegram_bot_api:smart_restart" "DRY_RUN smart-restart $UNIT (getMe OK, polling stale)"
    return 0
  fi
  log "smart-restart EXEC systemctl restart $UNIT"
  alert_ops "telegram_bot_api:smart_restart" "🔁 smart-restart $UNIT (getMe OK, polling looks dead)"
  systemctl restart "$UNIT" || log "ERROR restart failed"
}

if [[ "${TELEGRAM_BOT_API_HEALTH_SKIP_RESTART:-false}" != "true" ]]; then
  maybe_smart_restart
fi

[[ "$PROBE_OK" -eq 1 ]] && exit 0 || exit 1
