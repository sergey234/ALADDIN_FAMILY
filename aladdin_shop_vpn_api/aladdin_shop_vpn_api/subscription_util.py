from __future__ import annotations

import re
from pathlib import Path
from typing import Any

_PLACEHOLDER_RE = re.compile(r"\{([a-z_]+)\}")


def _substitute(template: str, values: dict[str, str]) -> str:
    def repl(m: re.Match[str]) -> str:
        key = m.group(1)
        return values.get(key, m.group(0))

    return _PLACEHOLDER_RE.sub(repl, template)


def subscription_values(
    *,
    settings: Any,
    opaque_token: str,
    xray_client_uuid: str | None,
) -> dict[str, str]:
    host = (getattr(settings, "vpn_xray_public_host", None) or "").strip()
    if not host:
        host = (getattr(settings, "vpn_wg_endpoint_host", None) or "").strip()
    xuuid = (xray_client_uuid or "").strip()
    if not xuuid:
        xuuid = (getattr(settings, "vpn_xray_default_client_uuid", None) or "").strip()
    return {
        "opaque_token": opaque_token,
        "xray_uuid": xuuid,
        "host": host,
        "port": str(int(getattr(settings, "vpn_xray_port", None) or 8443)),
        "pbk": (getattr(settings, "vpn_xray_reality_public_key", None) or "").strip(),
        "sid": (getattr(settings, "vpn_xray_reality_short_id", None) or "").strip(),
        "sni": (getattr(settings, "vpn_xray_reality_sni", None) or "www.microsoft.com").strip(),
        "fp": (getattr(settings, "vpn_xray_reality_fingerprint", None) or "chrome").strip(),
    }


def build_subscription_body(
    *,
    settings: Any,
    opaque_token: str,
    xray_client_uuid: str | None,
) -> str | None:
    """Тело GET /sub/<opaque>: шаблон из env, иначе файл, иначе None (→ 501)."""
    values = subscription_values(
        settings=settings,
        opaque_token=opaque_token,
        xray_client_uuid=xray_client_uuid,
    )
    inline = (getattr(settings, "vpn_subscribe_vless_template", None) or "").strip()
    if inline:
        return _substitute(inline, values).strip() + "\n"

    raw_file = (getattr(settings, "vpn_subscribe_body_file", None) or "").strip()
    if raw_file:
        path = Path(raw_file)
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            return _substitute(text, values)

    return None
