#!/usr/bin/env bash
# Remove per-user Xray client after vpn_expired (Happ / VLESS backup path).
# argv1 = telegram_user_id
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=wg-common.sh
source "${SCRIPT_DIR}/wg-common.sh"

wg_load_env || exit 1

TID="${1:?usage: xray-peer-down.sh <telegram_user_id>}"
[[ "$TID" =~ ^[0-9]+$ ]] || {
    echo "xray-peer-down: invalid telegram_user_id" >&2
    exit 1
}

XRAY_CONFIG="${XRAY_CONFIG_PATH:-/opt/xray/config.json}"
XRAY_SERVICE="${XRAY_SYSTEMD_UNIT:-xray.service}"

UUID="$(sqlite3 "$VPN_DB_PATH" \
    "SELECT COALESCE(xray_client_uuid,'') FROM vpn_accounts WHERE telegram_user_id = $TID LIMIT 1;")"

if [[ -z "$UUID" ]]; then
    exit 0
fi

if [[ -f "$XRAY_CONFIG" ]]; then
    python3 - "$XRAY_CONFIG" "$UUID" <<'PY'
import json
import sys

path, uid = sys.argv[1], sys.argv[2].strip().lower()
data = json.loads(open(path, encoding="utf-8").read())
changed = False
for ib in data.get("inbounds", []):
    if ib.get("protocol") != "vless":
        continue
    clients = ib.get("settings", {}).get("clients", [])
    new_clients = [c for c in clients if str(c.get("id", "")).lower() != uid]
    if len(new_clients) != len(clients):
        ib.setdefault("settings", {})["clients"] = new_clients
        changed = True
if changed:
    open(path, "w", encoding="utf-8").write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
PY
    systemctl reload "$XRAY_SERVICE" 2>/dev/null || systemctl restart "$XRAY_SERVICE" 2>/dev/null || true
fi

sqlite3 "$VPN_DB_PATH" \
    "UPDATE vpn_accounts SET xray_client_uuid = NULL, updated_at = datetime('now') WHERE telegram_user_id = ${TID};"

exit 0
