#!/usr/bin/env bash
# Run vpn-phone-drill on Contabo (+ optional MAIN check).
set -euo pipefail

KEY="${SSH_KEY:-$HOME/.ssh/aladdin_server}"
SSH_OPTS=(-o IdentitiesOnly=yes -i "$KEY")
RSYNC_SSH="ssh ${SSH_OPTS[*]}"
CONTABO="${BOT_HOST:-root@185.225.233.150}"
MAIN="${MAIN_HOST:-root@149.154.65.180}"
SRC="$(cd "$(dirname "$0")/../../aladdin_shop_vpn_api" && pwd)"
MODE="${1:-preflight}"

check_main_from_mac() {
  echo "==> MAIN bridge (from Mac)"
  ssh "${SSH_OPTS[@]}" "${MAIN}" 'systemctl is-active xray-bridge wg-quick@wg-bridge'
}

echo "==> sync vpn-phone-drill scripts to Contabo"
rsync -az -e "$RSYNC_SSH" \
  "${SRC}/deploy/scripts/vpn_phone_drill.sh" \
  "${SRC}/deploy/scripts/vpn_phone_drill_init_journal.py" \
  "${SRC}/deploy/scripts/vpn_cdn_phase_decision.py" \
  "${SRC}/deploy/scripts/vpn_integration_week_journal.py" \
  "${CONTABO}:/opt/aladdin-shop-vpn-api/deploy/scripts/"
rsync -az -e "$RSYNC_SSH" "${SRC}/deploy/var/integration-week-journal.template.json" \
  "${CONTABO}:/opt/aladdin-shop-vpn-api/deploy/var/"

ssh "${SSH_OPTS[@]}" "${CONTABO}" "chmod +x /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_phone_drill.sh"

if [[ "${MODE}" == "preflight" || "${MODE}" == "full" ]]; then
  check_main_from_mac
fi

echo "==> run vpn_phone_drill.sh ${MODE} on Contabo"
ssh "${SSH_OPTS[@]}" "${CONTABO}" \
  "bash /opt/aladdin-shop-vpn-api/deploy/scripts/vpn_phone_drill.sh ${MODE}"
