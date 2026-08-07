#!/usr/bin/env bash
# Move shop SSOT timers to Contabo; stop duplicate APIs on MAIN.
set -euo pipefail

SSH_KEY="${SSH_KEY:-$HOME/.ssh/aladdin_server}"
MAIN_HOST="${MAIN_HOST:-root@149.154.65.180}"
CONTABO_HOST="${CONTABO_HOST:-root@185.225.233.150}"
APP_ROOT="/opt/aladdin-telegram-shop-bot"

ssh_main() { ssh -i "$SSH_KEY" -o BatchMode=yes "$MAIN_HOST" "$@"; }
ssh_contabo() { ssh -i "$SSH_KEY" -o BatchMode=yes "$CONTABO_HOST" "$@"; }

echo "==> [1/4] MAIN: stop duplicate shop APIs and timers"
ssh_main bash -s <<'REMOTE'
set -euo pipefail
for unit in aladdin-partner-api aladdin-webhook-worker; do
  systemctl stop "$unit" 2>/dev/null || true
  systemctl disable "$unit" 2>/dev/null || true
done
for timer in fx-rate-sync.timer ops-watchdog.timer; do
  systemctl stop "$timer" 2>/dev/null || true
  systemctl disable "$timer" 2>/dev/null || true
done
echo "MAIN shop leftovers:"
systemctl is-active aladdin-partner-api aladdin-webhook-worker fx-rate-sync.timer ops-watchdog.timer 2>/dev/null || true
REMOTE

echo "==> [2/4] Contabo: install fx-rate-sync + ops-watchdog units"
ssh_contabo bash -s <<'REMOTE'
set -euo pipefail
APP_ROOT="/opt/aladdin-telegram-shop-bot"

cat > /etc/systemd/system/fx-rate-sync.service <<'UNIT'
[Unit]
Description=Update USD_RUB_RATE from CBR (+ markup)
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=/opt/aladdin-telegram-shop-bot/current_app
ExecStart=/opt/aladdin-telegram-shop-bot/venv/bin/python3 /opt/aladdin-telegram-shop-bot/current_app/scripts/update_usd_rub_rate.py --env-file /opt/aladdin-telegram-shop-bot/shared/.env --markup-rub 5 --usdt-rub-mode zero
ExecStartPost=/bin/systemctl restart aladdin-telegram-bot.service aladdin-partner-api.service aladdin-webhook-worker.service
UNIT

cat > /etc/systemd/system/fx-rate-sync.timer <<'UNIT'
[Unit]
Description=Run fx-rate-sync daily

[Timer]
OnCalendar=*-*-* 09:00:00
Persistent=true
Unit=fx-rate-sync.service

[Install]
WantedBy=timers.target
UNIT

cat > /etc/systemd/system/ops-watchdog.service <<'UNIT'
[Unit]
Description=ALADDIN Telegram Shop Ops Watchdog (one-shot)
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
WorkingDirectory=/opt/aladdin-telegram-shop-bot/current_app
EnvironmentFile=/opt/aladdin-telegram-shop-bot/shared/.env
ExecStart=/opt/aladdin-telegram-shop-bot/venv/bin/python -m bot.services.ops_watchdog
UNIT

cat > /etc/systemd/system/ops-watchdog.timer <<'UNIT'
[Unit]
Description=Run ALADDIN Telegram Shop Ops Watchdog every 2 minutes

[Timer]
OnBootSec=2min
OnUnitActiveSec=2min
AccuracySec=30s
Unit=ops-watchdog.service
Persistent=true

[Install]
WantedBy=timers.target
UNIT

systemctl daemon-reload
systemctl enable --now fx-rate-sync.timer ops-watchdog.timer
REMOTE

echo "==> [3/4] Contabo: sync USD_RUB_RATE from CBR now"
ssh_contabo "$APP_ROOT/venv/bin/python3" "$APP_ROOT/current_app/scripts/update_usd_rub_rate.py" \
  --env-file "$APP_ROOT/shared/.env" --markup-rub 5 --usdt-rub-mode zero
ssh_contabo systemctl restart aladdin-telegram-bot.service aladdin-partner-api.service aladdin-webhook-worker.service

echo "==> [4/4] Verify"
echo "--- MAIN ---"
ssh_main 'systemctl is-active aladdin-partner-api aladdin-webhook-worker fx-rate-sync.timer ops-watchdog.timer 2>/dev/null; grep USD_RUB_RATE /opt/aladdin-telegram-shop-bot/shared/.env 2>/dev/null || echo "(no .env)"'
echo "--- Contabo ---"
ssh_contabo 'systemctl is-active fx-rate-sync.timer ops-watchdog.timer aladdin-telegram-bot aladdin-partner-api aladdin-webhook-worker 2>/dev/null; grep USD_RUB_RATE /opt/aladdin-telegram-shop-bot/shared/.env'
echo "Done."
