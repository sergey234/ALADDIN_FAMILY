"""TI-04 + TI-04b — fuzzy typosquat detection + brand allowlist."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import urlparse

BRAND_ALLOWLIST: Set[str] = {
    "sberbank.ru",
    "www.sberbank.ru",
    "online.sberbank.ru",
    "sber.ru",
    "www.sber.ru",
    "tinkoff.ru",
    "www.tinkoff.ru",
    "www.tbank.ru",
    "tbank.ru",
    "vtb.ru",
    "www.vtb.ru",
    "alfabank.ru",
    "www.alfabank.ru",
    "gosuslugi.ru",
    "www.gosuslugi.ru",
    "nalog.gov.ru",
    "cbr.ru",
    "www.cbr.ru",
    "ozon.ru",
    "www.ozon.ru",
    "wildberries.ru",
    "www.wildberries.ru",
    "avito.ru",
    "www.avito.ru",
    "cdek.ru",
    "www.cdek.ru",
    "pochta.ru",
    "www.pochta.ru",
    "yandex.ru",
    "www.yandex.ru",
    "mail.ru",
    "www.mail.ru",
    "vk.com",
    "www.vk.com",
    "apple.com",
    "www.apple.com",
    "microsoft.com",
    "www.microsoft.com",
    "google.com",
    "www.google.com",
    "wikipedia.org",
    "www.wikipedia.org",
    "gov.ru",
    "www.gov.ru",
    "mos.ru",
    "www.mos.ru",
    "rbc.ru",
    "www.rbc.ru",
    "consultant.ru",
    "www.consultant.ru",
    "cloudflare.com",
    "www.cloudflare.com",
    "github.com",
    "www.github.com",
    "nordvpn.com",
    "www.nordvpn.com",
    "expressvpn.com",
    "www.expressvpn.com",
}

BRAND_TOKENS: Tuple[str, ...] = (
    "sber",
    "sberbank",
    "tinkoff",
    "tbank",
    "vtb",
    "alfa",
    "alfabank",
    "gosuslugi",
    "nalog",
    "ozon",
    "wildberries",
    "avito",
    "cdek",
    "pochta",
    "yandex",
    # EN / global brands (afhub-p1-02 lookalike)
    "paypal",
    "amazon",
    "apple",
    "google",
    "microsoft",
    "chase",
    "wellsfargo",
)

_SUSPICIOUS_TLDS = (".ru.com", ".com.ru", ".xyz", ".top", ".club", ".online", ".site", ".icu")
_PHISH_LABELS = ("login", "secure", "verify", "account", "auth", "update", "confirm", "wallet")


def _levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            ins = cur[j - 1] + 1
            delete = prev[j] + 1
            sub = prev[j - 1] + (ca != cb)
            cur.append(min(ins, delete, sub))
        prev = cur
    return prev[-1]


def _decode_punycode_host(host: str) -> str:
    parts: List[str] = []
    for label in host.split("."):
        if label.startswith("xn--"):
            try:
                parts.append(label.encode("ascii").decode("idna"))
            except Exception:
                parts.append(label)
        else:
            parts.append(label)
    return ".".join(parts)


def normalize_host(url_or_host: str) -> Optional[str]:
    raw = (url_or_host or "").strip().lower()
    if not raw:
        return None
    if "://" in raw:
        host = (urlparse(raw).hostname or "").lower()
    else:
        host = raw.split("/")[0].split(":")[0].lower()
    host = host.removeprefix("www.")
    if not host:
        return None
    host = _decode_punycode_host(host).lower()
    if not re.match(r"^[a-z0-9а-яё.\-]+$", host, re.IGNORECASE):
        if not re.match(r"^[a-z0-9.\-]+$", host):
            return None
    return host


def is_allowlisted(host: str) -> bool:
    h = (host or "").lower().removeprefix("www.")
    if not h:
        return False
    if h in BRAND_ALLOWLIST or f"www.{h}" in BRAND_ALLOWLIST:
        return True
    for allowed in BRAND_ALLOWLIST:
        if h == allowed.removeprefix("www."):
            return True
    return False


def _labels(host: str) -> List[str]:
    return [p for p in host.replace("_", "-").split(".") if p]


def analyze_fuzzy_url(url: str) -> Optional[Dict[str, Any]]:
    """Return fuzzy hit dict or None. Allowlisted hosts → None (never fake)."""
    host = normalize_host(url)
    if not host:
        return None
    if is_allowlisted(host):
        return None

    labels = _labels(host)
    if not labels:
        return None

    reasons: List[str] = []
    confidence = 0.0
    matched_brand: Optional[str] = None

    has_bad_tld = any(host.endswith(tld) for tld in _SUSPICIOUS_TLDS)
    joined = "-".join(labels)

    for brand in BRAND_TOKENS:
        padded = f"-{joined}-"
        if (
            brand in labels
            or f"-{brand}-" in padded
            or joined.startswith(f"{brand}-")
            or joined.endswith(f"-{brand}")
        ):
            matched_brand = brand
            reasons.append("fuzzy_brand_in_host")
            confidence = max(confidence, 0.82)
            break
        if len(brand) >= 4:
            for lab in labels:
                if len(lab) < 4:
                    continue
                dist = _levenshtein(lab, brand)
                if 1 <= dist <= 2:
                    matched_brand = brand
                    reasons.append("fuzzy_typosquat")
                    confidence = max(confidence, 0.8 if dist == 1 else 0.76)
                    break
        if matched_brand:
            break

    if any(lab in _PHISH_LABELS for lab in labels) and matched_brand:
        reasons.append("fuzzy_phish_label")
        confidence = max(confidence, 0.84)

    if has_bad_tld and matched_brand:
        reasons.append("fuzzy_suspicious_tld")
        confidence = max(confidence, 0.85)

    if "xn--" in (url or "").lower() and matched_brand:
        reasons.append("fuzzy_punycode")
        confidence = max(confidence, 0.86)

    if not matched_brand or confidence < 0.75:
        return None

    return {
        "host": host,
        "brand": matched_brand,
        "confidence": round(confidence, 3),
        "reason": "fuzzy_typosquat",
        "reasons": reasons[:6],
        "allowlisted": False,
    }
