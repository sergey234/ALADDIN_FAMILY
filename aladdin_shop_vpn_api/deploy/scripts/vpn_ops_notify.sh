#!/usr/bin/env bash
# Shared ops alerts: tech bot (@texAiMonkey_bot) + ADMIN_IDS fan-out (payment-style).
# Source from deploy/scripts/*.sh — do not run directly unless testing.
set -euo pipefail

VPN_OPS_STATE_DIR="${VPN_OPS_STATE_DIR:-/var/lib/aladdin-vpn-ops}"
VPN_OPS_DEDUPE_SEC="${VPN_OPS_DEDUPE_SEC:-${ALERT_COOLDOWN_SECONDS:-900}}"
# Digest slots are unique per day; still guard against double-fires within ~20h.
VPN_OPS_DIGEST_DEDUPE_SEC="${VPN_OPS_DIGEST_DEDUPE_SEC:-72000}"
VPN_SHARED_ENV="${VPN_SHARED_ENV:-/opt/aladdin-telegram-shop-bot/shared/.env}"

vpn_ops_load_env() {
  if [[ -f "$VPN_SHARED_ENV" ]]; then
    _env_get() {
      grep -m1 "^${1}=" "$VPN_SHARED_ENV" 2>/dev/null | cut -d= -f2- | tr -d '"' | tr -d "'"
    }
    TELEGRAM_TOKEN="$(_env_get TECH_ALERT_TELEGRAM_BOT_TOKEN)"
    TELEGRAM_CHAT="$(_env_get TECH_ALERT_TELEGRAM_CHAT_ID)"
    ALERT_TOKEN="$(_env_get ALERT_TELEGRAM_BOT_TOKEN)"
    ALERT_CHAT="$(_env_get ALERT_TELEGRAM_CHAT_ID)"
    ADMIN_IDS_RAW="$(_env_get ADMIN_IDS)"
    if [[ -z "${TELEGRAM_TOKEN:-}" || -z "${TELEGRAM_CHAT:-}" ]]; then
      TELEGRAM_TOKEN="${ALERT_TOKEN:-}"
      TELEGRAM_CHAT="${ALERT_CHAT:-}"
    fi
    STATUS_CHANNEL="$(_env_get VPN_STATUS_CHANNEL_POST_ID)"
    STATUS_CHANNEL_NOTIFY="$(_env_get VPN_STATUS_CHANNEL_NOTIFY_ENABLED)"
    ALERTS_ON="$(_env_get ALERTS_ENABLED)"
  else
    TELEGRAM_TOKEN="${TECH_ALERT_TELEGRAM_BOT_TOKEN:-${ALERT_TELEGRAM_BOT_TOKEN:-}}"
    TELEGRAM_CHAT="${TECH_ALERT_TELEGRAM_CHAT_ID:-${ALERT_TELEGRAM_CHAT_ID:-}}"
    ALERT_TOKEN="${ALERT_TELEGRAM_BOT_TOKEN:-}"
    ALERT_CHAT="${ALERT_TELEGRAM_CHAT_ID:-}"
    ADMIN_IDS_RAW="${ADMIN_IDS:-}"
    if [[ -z "${TELEGRAM_TOKEN:-}" || -z "${TELEGRAM_CHAT:-}" ]]; then
      TELEGRAM_TOKEN="${ALERT_TELEGRAM_BOT_TOKEN:-}"
      TELEGRAM_CHAT="${ALERT_TELEGRAM_CHAT_ID:-}"
    fi
    STATUS_CHANNEL="${VPN_STATUS_CHANNEL_POST_ID:-}"
    STATUS_CHANNEL_NOTIFY="${VPN_STATUS_CHANNEL_NOTIFY_ENABLED:-false}"
    ALERTS_ON="${ALERTS_ENABLED:-false}"
  fi
}

# Same recipients as payment order cards: all ADMIN_IDS (+ optional group chat).
vpn_ops_admin_recipients() {
  vpn_ops_load_env
  local raw="${ADMIN_IDS_RAW:-}"
  local -a out=()
  local part seen="|"
  if [[ -n "$raw" ]]; then
    raw="${raw//;/,}"
    IFS=',' read -r -a parts <<<"$raw"
    for part in "${parts[@]}"; do
      part="$(echo "$part" | tr -d '[:space:]')"
      [[ "$part" =~ ^[0-9-]+$ ]] || continue
      [[ "$seen" == *"|$part|"* ]] && continue
      seen+="${part}|"
      out+=("$part")
    done
  fi
  # Group ALERT chat (−100…) if configured — same as ops_order_notify.
  if [[ -n "${ALERT_CHAT:-}" && "$ALERT_CHAT" == -* ]]; then
    if [[ "$seen" != *"|${ALERT_CHAT}|"* ]]; then
      out+=("$ALERT_CHAT")
    fi
  fi
  if ((${#out[@]} == 0)) && [[ -n "${TELEGRAM_CHAT:-}" ]]; then
    out+=("$TELEGRAM_CHAT")
  fi
  printf '%s\n' "${out[@]}"
}

vpn_ops_status_channel_enabled() {
  vpn_ops_load_env
  [[ "${STATUS_CHANNEL_NOTIFY}" == "true" || "${STATUS_CHANNEL_NOTIFY}" == "1" ]] \
    && [[ -n "${STATUS_CHANNEL:-}" ]]
}

vpn_ops_ensure_state_dir() {
  mkdir -p "$VPN_OPS_STATE_DIR" 2>/dev/null || VPN_OPS_STATE_DIR="/tmp/aladdin-vpn-ops-state"
  mkdir -p "$VPN_OPS_STATE_DIR"
}

vpn_ops_dedupe_ok() {
  local key="$1"
  local window="${2:-$VPN_OPS_DEDUPE_SEC}"
  vpn_ops_ensure_state_dir
  local f="${VPN_OPS_STATE_DIR}/${key}.last"
  local now last
  now=$(date +%s)
  if [[ -f "$f" ]]; then
    last=$(cat "$f" 2>/dev/null || echo 0)
    if (( now - last < window )); then
      return 1
    fi
  fi
  echo "$now" >"$f"
  return 0
}

vpn_ops_tg_send() {
  local chat_id="$1"
  local text="$2"
  local token="${3:-${TELEGRAM_TOKEN:-}}"
  [[ -z "$token" || -z "$chat_id" ]] && return 0
  curl -fsS -m 15 -X POST "https://api.telegram.org/bot${token}/sendMessage" \
    -d "chat_id=${chat_id}" \
    -d "disable_web_page_preview=true" \
    --data-urlencode "text=${text}" >/dev/null 2>&1 || true
}

# Infra alert → TECH bot token, fan-out to all ADMIN_IDS (payment-style).
vpn_ops_alert() {
  local dedupe_key="$1"
  local text="$2"
  vpn_ops_load_env
  [[ "${ALERTS_ON}" != "true" && -z "${TELEGRAM_TOKEN:-}" ]] && return 0
  vpn_ops_dedupe_ok "$dedupe_key" || return 0
  local chat
  while IFS= read -r chat; do
    [[ -n "$chat" ]] || continue
    vpn_ops_tg_send "$chat" "$text" "$TELEGRAM_TOKEN"
  done < <(vpn_ops_admin_recipients)
}

# Command Center digest → prefer shop ALERT bot (same as payment cards) + ADMIN_IDS.
vpn_ops_digest() {
  local dedupe_key="$1"
  local text="$2"
  vpn_ops_load_env
  [[ "${ALERTS_ON}" != "true" && -z "${ALERT_TOKEN:-}${TELEGRAM_TOKEN:-}" ]] && return 0
  vpn_ops_dedupe_ok "$dedupe_key" "$VPN_OPS_DIGEST_DEDUPE_SEC" || return 0
  local token="${ALERT_TOKEN:-$TELEGRAM_TOKEN}"
  local chat
  while IFS= read -r chat; do
    [[ -n "$chat" ]] || continue
    vpn_ops_tg_send "$chat" "$text" "$token"
  done < <(vpn_ops_admin_recipients)
}

vpn_ops_status_channel_degraded() {
  local reason="$1"
  vpn_ops_status_channel_enabled || return 0
  vpn_ops_load_env
  vpn_ops_ensure_state_dir
  local f="${VPN_OPS_STATE_DIR}/status_degraded.last"
  if [[ -f "$f" ]]; then
    return 0
  fi
  touch "$f"
  local ts
  ts=$(date -u +"%H:%M UTC")
  local msg
  msg=$'⚠️ **VPN** — возможны обрывы или низкая скорость до '"${ts}"$'.\nПричина: '"${reason}"$'\nРекомендуем: обновить подписку в HitWave / v2rayNG или сменить профиль.\nОбновления — в этом канале.'
  vpn_ops_tg_send "$STATUS_CHANNEL" "$msg"
}

vpn_ops_status_channel_recovered() {
  vpn_ops_status_channel_enabled || return 0
  vpn_ops_load_env
  local f="${VPN_OPS_STATE_DIR}/status_degraded.last"
  [[ ! -f "$f" ]] && return 0
  rm -f "$f"
  vpn_ops_tg_send "$STATUS_CHANNEL" $'✅ Инцидент закрыт, VPN / магазин в штатном режиме.'
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  key="${1:-}"
  shift || true
  case "$key" in
    bridge-guard-fail)
      vpn_ops_alert "$key" "❌ VPN bridge guard FAILED on MAIN (hop SNI / routing / TCP 10.10.0.2). Log: /var/log/vpn-bridge-guard.log"
      vpn_ops_status_channel_degraded "bridge guard на MAIN"
      ;;
    sendq-high)
      vpn_ops_alert "$key" "❌ Send-Q watch FAILED on Contabo (downlink black hole :443?). Log: /var/log/vpn-sendq-watch.log"
      vpn_ops_status_channel_degraded "высокий Send-Q на :443"
      ;;
    device-binding-guard)
      msg="${*:-⚠️ VPN: сброшен тестовый HWID на protected TID (deploy smoke).}"
      vpn_ops_alert "$key" "$msg"
      ;;
    *)
      msg="${*:-VPN ops alert ($key)}"
      vpn_ops_alert "$key" "$msg"
      ;;
  esac
fi
