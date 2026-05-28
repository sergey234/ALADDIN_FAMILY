#!/usr/bin/env bash
# Re-apply wg peers from vpn.db (call from wg-quick PostUp after reboot). Idempotent.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=wg-common.sh
source "${SCRIPT_DIR}/wg-common.sh"

wg_load_env || exit 1

IFACE="${VPN_WG_INTERFACE:-wg0}"

while IFS='|' read -r pub tip; do
    [[ -z "$pub" || -z "$tip" ]] && continue
    wg set "$IFACE" peer "$pub" allowed-ips "${tip}/32" 2>/dev/null || true
done < <(
    sqlite3 -separator '|' "$VPN_DB_PATH" \
        "SELECT wg_client_public_key, wg_client_tunnel_ip FROM vpn_accounts WHERE status = 'vpn_active' AND wg_client_public_key IS NOT NULL AND TRIM(wg_client_public_key) != '' AND wg_client_tunnel_ip IS NOT NULL AND TRIM(wg_client_tunnel_ip) != '';"
)

exit 0
