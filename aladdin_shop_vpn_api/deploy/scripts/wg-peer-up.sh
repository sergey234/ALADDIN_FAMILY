#!/usr/bin/env bash
# After worker marks account vpn_active (stub or future native WG): add/replace WG peer.
# argv1 = telegram_user_id (digits only). Requires: wg, sqlite3, write access to VPN_DB_PATH and WG_KEYS_DIR.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=wg-common.sh
source "${SCRIPT_DIR}/wg-common.sh"

escape_sql_literal() {
    printf '%s' "$1" | sed "s/'/''/g"
}

wg_load_env || exit 1

TID="${1:?usage: wg-peer-up.sh <telegram_user_id>}"
[[ "$TID" =~ ^[0-9]+$ ]] || {
    echo "wg-peer-up: invalid telegram_user_id" >&2
    exit 1
}

mkdir -p "$WG_KEYS_DIR"
chmod 700 "$WG_KEYS_DIR" 2>/dev/null || true

PUB=$(sqlite3 "$VPN_DB_PATH" "SELECT COALESCE(wg_client_public_key,'') FROM vpn_accounts WHERE telegram_user_id = $TID LIMIT 1;")
TIP=$(sqlite3 "$VPN_DB_PATH" "SELECT COALESCE(wg_client_tunnel_ip,'') FROM vpn_accounts WHERE telegram_user_id = $TID LIMIT 1;")

ROW=$(sqlite3 "$VPN_DB_PATH" "SELECT COUNT(*) FROM vpn_accounts WHERE telegram_user_id = $TID;")
if [[ "${ROW:-0}" != "1" ]]; then
    echo "wg-peer-up: no vpn_accounts row for telegram_user_id=$TID" >&2
    exit 1
fi

if [[ -z "$PUB" ]]; then
    PRIV=$(wg genkey)
    PUB=$(printf '%s' "$PRIV" | wg pubkey | tr -d '\n\r')
    umask 077
    printf '%s\n' "$PRIV" >"${WG_KEYS_DIR}/${TID}.key"
    chmod 600 "${WG_KEYS_DIR}/${TID}.key"
    if [[ -n "${VPN_SERVICE_USER:-}" ]]; then
        chown "${VPN_SERVICE_USER}:${VPN_SERVICE_USER}" "${WG_KEYS_DIR}/${TID}.key" || true
    fi
fi
PUB=$(printf '%s' "$PUB" | tr -d '\n\r')
TIP=$(printf '%s' "$TIP" | tr -d '\n\r')

if [[ -z "$TIP" ]]; then
    OCT=$(wg_next_tunnel_host_octet)
    if [[ "$OCT" -lt 10 ]] || [[ "$OCT" -gt 250 ]]; then
        echo "wg-peer-up: no free tunnel host octet in 10.8.0.10–250 (got $OCT)" >&2
        exit 1
    fi
    TIP="10.8.0.${OCT}"
fi

EPUB=$(escape_sql_literal "$PUB")
ETIP=$(escape_sql_literal "$TIP")
sqlite3 "$VPN_DB_PATH" "UPDATE vpn_accounts SET wg_client_public_key = '${EPUB}', wg_client_tunnel_ip = '${ETIP}', updated_at = datetime('now') WHERE telegram_user_id = ${TID};"

IFACE="${VPN_WG_INTERFACE:-wg0}"
wg set "$IFACE" peer "$PUB" remove 2>/dev/null || true
wg set "$IFACE" peer "$PUB" allowed-ips "${TIP}/32"

if [[ -n "${VPN_SERVICE_USER:-}" ]] && [[ -f "${WG_KEYS_DIR}/${TID}.key" ]]; then
    chown "${VPN_SERVICE_USER}:${VPN_SERVICE_USER}" "${WG_KEYS_DIR}/${TID}.key" || true
fi

exit 0
