"""fws-04 — URL disinformation reasons + optional trust sources for verdict."""
from __future__ import annotations

import re
from typing import Any, Dict, List, Tuple
from urllib.parse import urlparse

# pattern regex → stable reason key (iOS: antifake_reason_<key>)
_URL_PATTERN_REASONS: Tuple[Tuple[str, str], ...] = (
    (r"@", "url_credential_trap"),
    (r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", "url_ip_address"),
    (r"login[-_]?secure", "url_phishing_path"),
    (r"verify[-_]?account", "url_phishing_path"),
    (r"\.ru\.com\b", "url_typosquat_tld"),
    (r"bit\.ly/", "url_shortener"),
    (r"tinyurl\.com/", "url_shortener"),
)

_SOURCE_CATALOG: Dict[str, Dict[str, str]] = {
    "phishing_awareness": {
        "id": "phishing_awareness",
        "title_key": "antifake_source_phishing_awareness",
        "title": "How to spot phishing links",
        "url": "https://consumer.ftc.gov/articles/how-recognize-and-avoid-phishing-scams",
    },
    "https_explainer": {
        "id": "https_explainer",
        "title_key": "antifake_source_https_explainer",
        "title": "Why HTTPS matters",
        "url": "https://www.cloudflare.com/learning/ssl/why-use-https/",
    },
    "shortener_risk": {
        "id": "shortener_risk",
        "title_key": "antifake_source_shortener_risk",
        "title": "Risks of shortened URLs",
        "url": "https://www.cisa.gov/news-events/news/avoiding-social-engineering-and-phishing-attacks",
    },
    "domain_verify": {
        "id": "domain_verify",
        "title_key": "antifake_source_domain_verify",
        "title": "Verify the official site before you sign in",
        "url": "https://www.icann.org/resources/pages/phishing-2013-05-03-en",
    },
    "independent_check": {
        "id": "independent_check",
        "title_key": "antifake_source_independent_check",
        "title": "Cross-check news with primary sources",
        "url": "https://www.reuters.com/fact-check/",
    },
}


def analyze_url_signals(url: str) -> Tuple[List[str], List[Dict[str, str]]]:
    """Return (reason_keys, sources[]) for a URL check."""
    raw = (url or "").strip()
    reasons: List[str] = []
    source_ids: List[str] = []

    for pattern, reason_key in _URL_PATTERN_REASONS:
        if re.search(pattern, raw, re.IGNORECASE) and reason_key not in reasons:
            reasons.append(reason_key)

    if raw.lower().startswith("http://"):
        if "insecure_http" not in reasons:
            reasons.append("insecure_http")
        source_ids.append("https_explainer")

    if any(r in reasons for r in ("url_phishing_path", "url_credential_trap", "url_typosquat_tld")):
        source_ids.append("phishing_awareness")
        source_ids.append("domain_verify")

    if "url_shortener" in reasons:
        source_ids.append("shortener_risk")

    if "url_ip_address" in reasons:
        source_ids.append("phishing_awareness")

    host = (urlparse(raw).hostname or "").lower()
    if not reasons:
        reasons = ["url_looks_neutral"]
        if host and not host.endswith((".gov", ".edu")):
            source_ids.append("independent_check")

    sources = [_SOURCE_CATALOG[sid] for sid in _dedupe(source_ids) if sid in _SOURCE_CATALOG]
    return reasons[:8], sources[:4]


def merge_sources(
    primary: List[Dict[str, str]],
    extra: Any,
) -> List[Dict[str, str]]:
    merged = list(primary)
    seen = {s.get("id") for s in merged if s.get("id")}
    if not isinstance(extra, list):
        return merged
    for item in extra:
        if not isinstance(item, dict):
            continue
        sid = str(item.get("id") or "")
        url = str(item.get("url") or "").strip()
        if not url:
            continue
        if sid and sid in seen:
            continue
        merged.append(
            {
                "id": sid or None,
                "title_key": item.get("title_key"),
                "title": str(item.get("title") or url)[:200],
                "url": url[:2048],
            }
        )
        if sid:
            seen.add(sid)
        if len(merged) >= 6:
            break
    return merged


def _dedupe(items: List[str]) -> List[str]:
    out: List[str] = []
    for item in items:
        if item not in out:
            out.append(item)
    return out
