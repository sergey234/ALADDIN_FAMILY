#!/usr/bin/env bash
# After expire/revoke to vpn_expired: remove peer and clear WG fields (client may re-provision with fresh keys).
# argv1 = telegram_user_id (digits only).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=wg-common.sh
source "${SCRIPT_DIR}/wg-common.sh"

wg_load_env || exit 1

TID="${1:?usage: wg-peer-down.sh <telegram_user_id>}"
[[ "$TID" =~ ^[0-9]+$ ]] || {
    echo "wg-peer-down: invalid telegram_user_id" >&2
    exit 1
}

PUB=$(sqlite3 "$VPN_DB_PATH" "SELECT COALESCE(wg_client_public_key,'') FROM vpn_accounts WHERE telegram_user_id = $TID LIMIT 1;")
IFACE="${VPN_WG_INTERFACE:-wg0}"

if [[ -n "$PUB" ]]; then
    wg set "$IFACE" peer "$PUB" remove 2>/dev/null || true
fi

rm -f "${WG_KEYS_DIR:-/opt/aladdin-shop-vpn-api/var/wg-keys}/${TID}.key"

sqlite3 "$VPN_DB_PATH" "UPDATE vpn_accounts SET wg_client_public_key = NULL, wg_client_tunnel_ip = NULL, updated_at = datetime('now') WHERE telegram_user_id = ${TID};"

exit 0
