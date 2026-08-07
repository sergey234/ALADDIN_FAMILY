#!/usr/bin/env bash
# Деплой Telegram Shop Bot на production.
# КАНОН: polling только Contabo; MAIN — API/worker, бот ЗАМАСКИРОВАН.
set -euo pipefail

BOT_HOST="${BOT_HOST:-root@185.225.233.150}"
API_HOST="${API_HOST:-root@149.154.65.180}"
SSH_KEY="${SSH_KEY:-$HOME/.ssh/aladdin_server}"
ROOT="/opt/aladdin-telegram-shop-bot"
TS="$(date +%Y%m%d-%H%M%S)"
SRC="$(cd "$(dirname "$0")/.." && pwd)"

SSH_OPTS=(-o IdentitiesOnly=yes -i "$SSH_KEY")

ensure_env_flag() {
  local host="$1" key="$2" value="$3"
  ssh "${SSH_OPTS[@]}" "$host" bash -s <<EOF
set -e
ENV="${ROOT}/shared/.env"
touch "\$ENV"
if grep -q "^${key}=" "\$ENV" 2>/dev/null; then
  sed -i 's/^${key}=.*/${key}=${value}/' "\$ENV"
else
  echo "${key}=${value}" >> "\$ENV"
fi
EOF
}

echo "==> Release ${TS}"
echo "    source: ${SRC}"
echo "    bot:    ${BOT_HOST}"
echo "    api:    ${API_HOST}"

deploy_tree() {
  local host="$1"
  ssh "${SSH_OPTS[@]}" "$host" "mkdir -p ${ROOT}/releases/${TS}/telegram_stars_shop_bot"
  rsync -az --delete \
    --exclude '.git' --exclude '__pycache__' --exclude '*.pyc' \
    --exclude '.venv' --exclude 'venv' --exclude 'data' --exclude '.env' \
    -e "ssh ${SSH_OPTS[*]}" \
    "${SRC}/" "${host}:${ROOT}/releases/${TS}/telegram_stars_shop_bot/"
  ssh "${SSH_OPTS[@]}" "$host" bash -s <<EOF
set -e
ln -sfn "${ROOT}/releases/${TS}" "${ROOT}/current_release"
ln -sfn "${ROOT}/releases/${TS}/telegram_stars_shop_bot" "${ROOT}/current_app"
echo "current_app -> \$(readlink -f ${ROOT}/current_app)"
EOF
}

echo "==> Contabo: code + enable bot + restart"
deploy_tree "$BOT_HOST"
ensure_env_flag "$BOT_HOST" "SHOP_BOT_POLLING_ENABLED" "true"
ensure_env_flag "$BOT_HOST" "UI_SHOW_VPN" "true"
ensure_env_flag "$BOT_HOST" "REF_BUYER_FIRST_ORDER_DISCOUNT_PERCENT" "0"
ensure_env_flag "$BOT_HOST" "UI_SHOW_GIFTS" "false"
ensure_env_flag "$BOT_HOST" "FEATURE_FEEDBACK_COLLECTION_ENABLED" "true"
ensure_env_flag "$BOT_HOST" "STUCK_PAID_FAST_ALERT_MINUTES" "5"
ensure_env_flag "$BOT_HOST" "LAVA_RECONCILE_INTERVAL_SECONDS" "30"
ensure_env_flag "$BOT_HOST" "AUTO_FULFILL_SUCCESS_ALERTS_ENABLED" "true"
ensure_env_flag "$BOT_HOST" "ADMIN_BOT_ALERTS_ENABLED" "true"
ensure_env_flag "$BOT_HOST" "ISTAR_ORDER_POLL_INTERVAL_SECONDS" "120"
ensure_env_flag "$BOT_HOST" "ISTAR_ORDER_POLL_MIN_PROCESSING_MINUTES" "3"
ensure_env_flag "$BOT_HOST" "MAX_PENDING_PAYMENT_ORDERS_PER_USER" "3"
ensure_env_flag "$BOT_HOST" "AUTO_EXPIRE_OTHER_PENDING_ON_NEW_ORDER" "true"
ensure_env_flag "$BOT_HOST" "VPN_REFERRAL_REFERRER_DAYS" "3"
ensure_env_flag "$BOT_HOST" "VPN_REFERRAL_FRIEND_DAYS" "7"
ensure_env_flag "$BOT_HOST" "VPN_TRIAL_REFERRAL_REFERRER_DAYS" "1"
ensure_env_flag "$BOT_HOST" "VPN_TRIAL_REFERRAL_FRIEND_DAYS" "3"
# Канон 2026-07-28: бонус spend на всё; антиабуз через вывод/уровни
ensure_env_flag "$BOT_HOST" "REF_BONUS_VPN_ONLY" "false"
ssh "${SSH_OPTS[@]}" "$BOT_HOST" bash -s <<'EOF'
set -e
ROOT=/opt/aladdin-telegram-shop-bot
touch "${ROOT}/SHOP_BOT_POLLING_HOST"
mkdir -p /etc/systemd/system/aladdin-telegram-bot.service.d
cat > /etc/systemd/system/aladdin-telegram-bot.service.d/50-contabo-only.conf <<'UNIT'
[Unit]
ConditionPathExists=/opt/aladdin-telegram-shop-bot/SHOP_BOT_POLLING_HOST
UNIT
systemctl daemon-reload
systemctl enable aladdin-telegram-bot.service
systemctl restart aladdin-telegram-bot.service aladdin-partner-api.service aladdin-webhook-worker.service
systemctl is-active aladdin-telegram-bot.service
EOF

echo "==> MAIN: code sync + block bot start (no polling host marker)"
deploy_tree "$API_HOST"
ensure_env_flag "$API_HOST" "UI_SHOW_VPN" "false"
ensure_env_flag "$API_HOST" "UI_SHOW_GIFTS" "false"
ssh "${SSH_OPTS[@]}" "$API_HOST" bash -s <<'EOF'
set -e
ROOT=/opt/aladdin-telegram-shop-bot
rm -f "${ROOT}/SHOP_BOT_POLLING_HOST"
mkdir -p /etc/systemd/system/aladdin-telegram-bot.service.d
cat > /etc/systemd/system/aladdin-telegram-bot.service.d/50-contabo-only.conf <<'UNIT'
[Unit]
# Polling только где есть маркер (Contabo). Без файла unit не стартует.
ConditionPathExists=/opt/aladdin-telegram-shop-bot/SHOP_BOT_POLLING_HOST
UNIT
systemctl daemon-reload
systemctl stop aladdin-telegram-bot.service 2>/dev/null || true
systemctl disable aladdin-telegram-bot.service 2>/dev/null || true
systemctl start aladdin-telegram-bot.service 2>/dev/null || true
st=$(systemctl is-active aladdin-telegram-bot.service 2>/dev/null || echo dead)
if [ "$st" = "active" ]; then
  echo "ERROR: MAIN bot started — remove SHOP_BOT_POLLING_HOST" >&2
  systemctl stop aladdin-telegram-bot.service
  exit 1
fi
systemctl restart aladdin-partner-api.service aladdin-webhook-worker.service
systemctl is-active aladdin-partner-api.service
curl -s -m 8 http://127.0.0.1:8090/health
EOF

echo "==> Post-deploy verify"
chmod +x "${SRC}/scripts/verify_single_bot.sh"
"${SRC}/scripts/verify_single_bot.sh"

echo "==> OK deployed ${TS}"

echo "==> auto-fulfill worker placement"
scp "${SSH_OPTS[@]}" "${SRC}/docs/auto-fulfill-worker.service" "${BOT_HOST}:/etc/systemd/system/auto-fulfill-worker.service"
ssh "${SSH_OPTS[@]}" "$BOT_HOST" 'systemctl daemon-reload && systemctl enable --now auto-fulfill-worker.service && systemctl is-active auto-fulfill-worker.service'
ssh "${SSH_OPTS[@]}" "$API_HOST" 'systemctl stop auto-fulfill-worker.service 2>/dev/null || true; systemctl disable auto-fulfill-worker.service 2>/dev/null || true; systemctl is-active auto-fulfill-worker.service 2>&1 || echo MAIN_AUTO_FF_OFF'
