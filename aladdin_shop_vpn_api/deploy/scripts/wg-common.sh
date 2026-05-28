# shellcheck shell=bash
# Shared helpers for wg-peer-*.sh and wg-resync-active-peers.sh (source from same directory).

wg_load_env() {
    local _env="${VPN_ENV_FILE:-/opt/aladdin-shop-vpn-api/env}"
    if [[ -f "$_env" ]]; then
        # shellcheck disable=SC1090
        set -a && source "$_env" && set +a
    fi
    if [[ -z "${VPN_DB_PATH:-}" ]]; then
        echo "wg-common: VPN_DB_PATH is not set (export or set in ${VPN_ENV_FILE:-/opt/aladdin-shop-vpn-api/env})" >&2
        return 1
    fi
    export VPN_WG_INTERFACE="${VPN_WG_INTERFACE:-wg0}"
    export WG_KEYS_DIR="${WG_KEYS_DIR:-/opt/aladdin-shop-vpn-api/var/wg-keys}"
    return 0
}

wg_next_tunnel_host_octet() {
    # Префикс пула всегда «10.8.0.» (7 символов); последний октет — с позиции 8.
    sqlite3 "$VPN_DB_PATH" \
        "SELECT COALESCE((SELECT MAX(CAST(SUBSTR(wg_client_tunnel_ip, 8) AS INTEGER)) FROM vpn_accounts WHERE wg_client_tunnel_ip GLOB '10.8.0.*'), 9) + 1;"
}
