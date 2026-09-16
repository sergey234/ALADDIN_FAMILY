#!/usr/bin/env bash
# Install Command Center timer on Brain (Contabo). Idempotent.
# Copies units from this repo tree; overlays scripts onto /opt/.../deploy/scripts/.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UNIT_SRC="${ROOT}/systemd"
DST=/etc/systemd/system
SCRIPTS_DST=/opt/aladdin-shop-vpn-api/deploy/scripts

install -m 0644 "${UNIT_SRC}/aladdin-vpn-ops-command-center.service" \
  "${DST}/aladdin-vpn-ops-command-center.service"
install -m 0644 "${UNIT_SRC}/aladdin-vpn-ops-command-center.timer" \
  "${DST}/aladdin-vpn-ops-command-center.timer"

for f in vpn_ops_command_center.py vpn_ops_command_center.sh vpn_ops_notify.sh \
  vpn_bridge_peers_daily_report.sh; do
  if [[ -f "${ROOT}/scripts/${f}" ]]; then
    install -m 0755 "${ROOT}/scripts/${f}" "${SCRIPTS_DST}/${f}"
  fi
done

cat >"${DST}/aladdin-vpn-zombie-daily.service" <<'UNIT'
[Unit]
Description=Send evening VPN OPS Command Center report to ADMIN_IDS
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
Environment=VPN_SHARED_ENV=/opt/aladdin-telegram-shop-bot/shared/.env
Environment=ALERTS_ENABLED=true
ExecStart=/opt/aladdin-shop-vpn-api/deploy/scripts/vpn_ops_command_center.sh evening
NoNewPrivileges=true
PrivateTmp=true
ProtectHome=true
ProtectSystem=strict
ReadWritePaths=/var/lib/aladdin-vpn-ops /opt/aladdin-shop-vpn-api/var
UNIT

systemctl daemon-reload
systemctl enable --now aladdin-vpn-ops-command-center.timer
if systemctl list-unit-files aladdin-vpn-zombie-daily.timer 2>/dev/null | grep -q aladdin-vpn-zombie-daily.timer; then
  systemctl disable --now aladdin-vpn-zombie-daily.timer || true
fi

systemctl list-timers aladdin-vpn-ops-command-center.timer --no-pager
echo "OK: Command Center timer installed (09/14/21 Europe/Moscow)"
