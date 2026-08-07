"""Validate WireGuard .conf from vpn-api before delivery to user."""

from __future__ import annotations

import re

_WG_ENDPOINT_RE = re.compile(r"^Endpoint\s*=\s*(.+)$", re.MULTILINE)
_WG_ALLOWED_RE = re.compile(r"^AllowedIPs\s*=\s*(.+)$", re.MULTILINE)
_WG_DNS_RE = re.compile(r"^DNS\s*=\s*(.+)$", re.MULTILINE)


def wg_conf_validate(conf: str) -> tuple[bool, list[str]]:
    """
    Return (ok, issues). ok=True when conf matches post-fix server contract.
    """
    text = (conf or "").strip()
    issues: list[str] = []
    if not text or "[Interface]" not in text:
        return False, ["пустой или не WireGuard .conf"]

    if "::/0" in text:
        issues.append("AllowedIPs содержит ::/0 — удалите туннель и запросите новый файл")

    endpoint_m = _WG_ENDPOINT_RE.search(text)
    if not endpoint_m:
        issues.append("нет строки Endpoint")
    else:
        ep = endpoint_m.group(1).strip()
        if ":51820" in ep:
            issues.append(f"устаревший Endpoint {ep} — нужен порт :443")
        elif not ep.endswith(":443"):
            issues.append(f"Endpoint {ep} — ожидается UDP :443")

    allowed_m = _WG_ALLOWED_RE.search(text)
    if not allowed_m:
        issues.append("нет AllowedIPs")
    else:
        allowed = allowed_m.group(1).strip()
        has_full_v4 = "0.0.0.0/0" in allowed or (
            "0.0.0.0/1" in allowed and "128.0.0.0/1" in allowed
        )
        if not has_full_v4:
            issues.append(f"AllowedIPs={allowed} — нужен 0.0.0.0/0 или 0.0.0.0/1, 128.0.0.0/1")
        if "::" in allowed:
            issues.append("AllowedIPs не должен содержать IPv6")

    dns_m = _WG_DNS_RE.search(text)
    if not dns_m:
        issues.append("нет DNS — нужен 10.8.0.1")
    elif "10.8.0.1" not in dns_m.group(1):
        issues.append(f"DNS={dns_m.group(1).strip()} — ожидается 10.8.0.1")

    return len(issues) == 0, issues


def wg_conf_validate_summary_html(conf: str) -> str:
    ok, issues = wg_conf_validate(conf)
    if ok:
        ep = (_WG_ENDPOINT_RE.search(conf or "") or [None, ""])[1] if conf else ""
        return (
            "<b>✅ Ключ WireGuard актуален</b>\n"
            f"Endpoint <code>{ep.strip()}</code> · IPv4-only · DNS <code>10.8.0.1</code>"
        )
    lines = ["<b>⚠️ Проверьте ключ WireGuard</b>"]
    lines.extend(f"• {issue}" for issue in issues)
    return "\n".join(lines)
