#!/usr/bin/env python3
"""Idempotent merge of VPN30 / subscription env keys into /opt/aladdin-shop-vpn-api/env."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ENV_PATH = Path(sys.argv[1] if len(sys.argv) > 1 else "/opt/aladdin-shop-vpn-api/env")
XRAY_CONFIG = Path(sys.argv[2] if len(sys.argv) > 2 else "/opt/xray/config.json")


def main() -> int:
    text = ENV_PATH.read_text(encoding="utf-8") if ENV_PATH.is_file() else ""

    def get_var(name: str) -> str:
        m = re.search(rf"^{re.escape(name)}=(.*)$", text, re.M)
        if not m:
            return ""
        v = m.group(1).strip()
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            v = v[1:-1]
        return v

    def _env_line(name: str, value: str) -> str:
        if re.search(r'[\s#&;|"\']', value) or value.startswith("["):
            esc = value.replace("\\", "\\\\").replace('"', '\\"')
            return f'{name}="{esc}"'
        return f"{name}={value}"

    def set_or_append(name: str, value: str) -> None:
        nonlocal text
        line = _env_line(name, value)
        if re.search(rf"^{re.escape(name)}=", text, re.M):
            text = re.sub(rf"^{re.escape(name)}=.*$", line, text, flags=re.M)
        else:
            if text and not text.endswith("\n"):
                text += "\n"
            text += line + "\n"

    xc = json.loads(XRAY_CONFIG.read_text(encoding="utf-8"))
    ib = next((x for x in xc.get("inbounds", []) if x.get("protocol") == "vless"), {})
    rs = ib.get("streamSettings", {}).get("realitySettings", {})
    clients = ib.get("settings", {}).get("clients", [])
    client_uuid = clients[0]["id"] if clients else ""
    pbk = rs.get("publicKey") or ""
    if isinstance(pbk, list):
        pbk = pbk[0] if pbk else ""
    short_ids = rs.get("shortIds") or rs.get("shortId") or []
    sid = short_ids[0] if isinstance(short_ids, list) and short_ids else str(short_ids or "")
    sni = (rs.get("serverNames") or ["www.microsoft.com"])[0]

    set_or_append("VPN_WG_CLIENT_MTU", "1280")
    set_or_append("VPN_XRAY_PUBLIC_HOST", get_var("VPN_WG_ENDPOINT_HOST") or "aladdin-ai.ru")
    set_or_append("VPN_XRAY_PORT", str(ib.get("port") or 8443))
    if client_uuid:
        set_or_append("VPN_XRAY_DEFAULT_CLIENT_UUID", client_uuid)
    if pbk:
        set_or_append("VPN_XRAY_REALITY_PUBLIC_KEY", pbk)
    if sid:
        set_or_append("VPN_XRAY_REALITY_SHORT_ID", sid)
    set_or_append("VPN_XRAY_REALITY_SNI", sni)

    nodes = [
        {
            "id": "primary",
            "wg_host": get_var("VPN_WG_ENDPOINT_HOST") or "149.154.65.180",
            "wg_port": int(get_var("VPN_WG_LISTEN_PORT") or 51820),
            "reality_port": int(ib.get("port") or 8443),
            "ovpn_port": 1194,
            "active": True,
        },
        {
            "id": "secondary",
            "wg_host": "",
            "wg_port": 51820,
            "reality_port": 8443,
            "ovpn_port": 1194,
            "active": False,
        },
    ]
    set_or_append("VPN_EGRESS_NODES_JSON", json.dumps(nodes, ensure_ascii=False))

    wg_host = get_var("VPN_WG_ENDPOINT_HOST") or "aladdin-ai.ru"
    loc_labels = [
        "🇪🇺 Автовыбор",
        "🇫🇷 Франция",
        "🇩🇪 Германия",
        "🇳🇱 Нидерланды",
        "🇮🇹 Италия",
        "🇭🇺 Венгрия",
        "🇬🇧 Великобритания",
        "🇺🇸 США",
    ]
    loc_items = []
    for i, label in enumerate(loc_labels):
        slug = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")[:48] or f"loc-{i}"
        loc_items.append({"slug": slug, "label": label, "endpoint_host": wg_host})
    set_or_append(
        "VPN_LOCATIONS_JSON",
        json.dumps({"preview_n": 3, "items": loc_items}, ensure_ascii=False),
    )

    sub_file = get_var("VPN_SUBSCRIBE_BODY_FILE")
    if sub_file and Path(sub_file).is_file() and not get_var("VPN_SUBSCRIBE_VLESS_TEMPLATE"):
        tpl = Path(sub_file).read_text(encoding="utf-8").strip()
        set_or_append("VPN_SUBSCRIBE_VLESS_TEMPLATE", tpl)

    ENV_PATH.write_text(text, encoding="utf-8")
    print("ok", ENV_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
