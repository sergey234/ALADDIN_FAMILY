#!/usr/bin/env bash
# Проверка: Shop Bot (@AiMonkeyStars_bot) — ровно один getUpdates на Contabo.
set -euo pipefail

KEY="${SSH_KEY:-$HOME/.ssh/aladdin_server}"
SSH_OPTS=(-o IdentitiesOnly=yes -i "$KEY")
MAIN="${MAIN_HOST:-root@149.154.65.180}"
CONTABO="${BOT_HOST:-root@185.225.233.150}"
FAIL=0

check() {
  local name="$1"
  shift
  if "$@"; then
    echo "OK  $name"
  else
    echo "FAIL $name"
    FAIL=1
  fi
}

main_bot_inactive() {
  local st
  st=$(ssh "${SSH_OPTS[@]}" "$MAIN" "systemctl is-active aladdin-telegram-bot.service 2>/dev/null || true")
  [[ "$st" == "inactive" ]]
}

main_bot_disabled() {
  local st
  st=$(ssh "${SSH_OPTS[@]}" "$MAIN" "systemctl is-enabled aladdin-telegram-bot.service 2>/dev/null || true")
  [[ "$st" == "disabled" || "$st" == "masked" ]]
}

main_bot_wont_start() {
  ssh "${SSH_OPTS[@]}" "$MAIN" 'systemctl start aladdin-telegram-bot.service 2>/dev/null || true
st=$(systemctl is-active aladdin-telegram-bot.service 2>/dev/null | tr -d "\n") || st=dead
test "$st" = inactive || test "$st" = failed || test "$st" = dead'
}

main_no_bot_process() {
  ssh "${SSH_OPTS[@]}" "$MAIN" "pgrep -af '[b]ot.main'" >/dev/null 2>&1 && return 1 || return 0
}

contabo_bot_active() {
  ssh "${SSH_OPTS[@]}" "$CONTABO" "systemctl is-active aladdin-telegram-bot.service" 2>&1 | grep -q '^active$'
}

contabo_one_process() {
  local n
  n=$(ssh "${SSH_OPTS[@]}" "$CONTABO" "pgrep -cf '[b]ot.main'" 2>/dev/null || echo 0)
  [[ "$n" == "1" ]]
}

no_telegram_conflict() {
  ! ssh "${SSH_OPTS[@]}" "$CONTABO" "tail -n 80 /opt/aladdin-telegram-shop-bot/logs/bot.log" 2>/dev/null | grep -q 'TelegramConflictError'
}

echo "=== verify_single_bot ==="
check "MAIN bot inactive" main_bot_inactive
check "MAIN bot disabled" main_bot_disabled
check "MAIN bot cannot start (no marker)" main_bot_wont_start
check "MAIN no bot.main process" main_no_bot_process
check "Contabo bot active" contabo_bot_active
check "Contabo exactly one bot.main" contabo_one_process
check "No recent TelegramConflictError" no_telegram_conflict

if [[ "$FAIL" -ne 0 ]]; then
  echo "=== FAILED ==="
  exit 1
fi
echo "=== ALL OK ==="
