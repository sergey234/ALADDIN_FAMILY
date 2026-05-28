#!/usr/bin/env bash
# Ensure per-user UUID exists in vpn.db and Xray vless clients[] (after provision).
# argv1 = telegram_user_id
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=wg-common.sh
source "${SCRIPT_DIR}/wg-common.sh"

wg_load_env || exit 1

TID="${1:?usage: xray-peer-up.sh <telegram_user_id>}"
[[ "$TID" =~ ^[0-9]+$ ]] || {
    echo "xray-peer-up: invalid telegram_user_id" >&2
    exit 1
}

XRAY_CONFIG="${XRAY_CONFIG_PATH:-/opt/xray/config.json}"
XRAY_SERVICE="${XRAY_SYSTEMD_UNIT:-xray.service}"

UUID="$(sqlite3 "$VPN_DB_PATH" \
    "SELECT COALESCE(xray_client_uuid,'') FROM vpn_accounts WHERE telegram_user_id = $TID LIMIT 1;")"

if [[ -z "$UUID" ]]; then
    UUID="$(python3 -c 'import uuid; print(uuid.uuid4())')"
    sqlite3 "$VPN_DB_PATH" \
        "UPDATE vpn_accounts SET xray_client_uuid = '$UUID', updated_at = datetime('now') WHERE telegram_user_id = ${TID};"
fi

if [[ ! -f "$XRAY_CONFIG" ]]; then
    exit 0
fi

python3 - "$XRAY_CONFIG" "$UUID" <<'PY'
import json
import sys

path, uid = sys.argv[1], sys.argv[2].strip()
data = json.loads(open(path, encoding="utf-8").read())
changed = False
for ib in data.get("inbounds", []):
    if ib.get("protocol") != "vless":
        continue
    clients = ib.setdefault("settings", {}).setdefault("clients", [])
    ids = {str(c.get("id", "")).lower() for c in clients}
    if uid.lower() not in ids:
        clients.append({"id": uid, "flow": "xtls-rprx-vision", "email": f"vpn-{uid[:8]}"})
        changed = True
if changed:
    open(path, "w", encoding="utf-8").write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
PY

systemctl reload "$XRAY_SERVICE" 2>/dev/null || systemctl restart "$XRAY_SERVICE" 2>/dev/null || true
exit 0
