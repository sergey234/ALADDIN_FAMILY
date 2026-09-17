"""afhub-p1-02 — follow URL redirects (bounded) + brand lookalike on final host.

SSRF: every hop must pass validate_check_url. Network optional — fails soft.
"""
from __future__ import annotations

import os
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin, urlparse

from app.services.antifake_security import AntifakeSecurityError, validate_check_url
from app.services.antifake_url_fuzzy import (
    BRAND_TOKENS,
    analyze_fuzzy_url,
    is_allowlisted,
    normalize_host,
)

MAX_REDIRECT_HOPS = 3
REDIRECT_TIMEOUT_SEC = 2.0


def _redirects_enabled() -> bool:
    return os.getenv("ANTIFAKE_URL_FOLLOW_REDIRECTS", "1").strip() not in (
        "0",
        "false",
        "False",
        "no",
    )


def _host_of(url: str) -> str:
    return (normalize_host(url) or "").lower()


def probe_redirect_chain(
    url: str,
    *,
    max_hops: int = MAX_REDIRECT_HOPS,
    timeout: float = REDIRECT_TIMEOUT_SEC,
) -> Dict[str, Any]:
    """Walk Location headers without downloading bodies.

    Returns dict:
      hops: list[str]
      final_url: str
      reasons: list[str]
      blocked: bool
    """
    reasons: List[str] = []
    hops: List[str] = []
    current = url
    try:
        current = validate_check_url(url)
    except AntifakeSecurityError:
        return {
            "hops": [],
            "final_url": url,
            "reasons": ["blocked_url"],
            "blocked": True,
        }

    hops.append(current)
    if not _redirects_enabled():
        return {
            "hops": hops,
            "final_url": current,
            "reasons": [],
            "blocked": False,
            "skipped": True,
        }

    try:
        import urllib.error
        import urllib.request
    except ImportError:
        return {
            "hops": hops,
            "final_url": current,
            "reasons": [],
            "blocked": False,
            "skipped": True,
        }

    class _NoRedirect(urllib.request.HTTPRedirectHandler):
        def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
            return None

    opener = urllib.request.build_opener(_NoRedirect)
    opener.addheaders = [("User-Agent", "ALADDIN-Antifake/1.0")]

    for _ in range(max(1, max_hops)):
        loc = None
        try:
            req = urllib.request.Request(current, method="HEAD")
            with opener.open(req, timeout=timeout) as resp:
                code = getattr(resp, "status", None) or resp.getcode()
                if code in (301, 302, 303, 307, 308):
                    loc = resp.headers.get("Location")
                else:
                    break
        except urllib.error.HTTPError as exc:
            if exc.code in (301, 302, 303, 307, 308):
                loc = exc.headers.get("Location") if exc.headers else None
            else:
                # try GET for servers that reject HEAD
                try:
                    req = urllib.request.Request(current, method="GET")
                    with opener.open(req, timeout=timeout) as resp:
                        code = getattr(resp, "status", None) or resp.getcode()
                        if code not in (301, 302, 303, 307, 308):
                            break
                        loc = resp.headers.get("Location")
                except urllib.error.HTTPError as exc2:
                    if exc2.code not in (301, 302, 303, 307, 308):
                        break
                    loc = exc2.headers.get("Location") if exc2.headers else None
                except Exception:
                    break
        except Exception:
            try:
                req = urllib.request.Request(current, method="GET")
                with opener.open(req, timeout=timeout) as resp:
                    code = getattr(resp, "status", None) or resp.getcode()
                    if code not in (301, 302, 303, 307, 308):
                        break
                    loc = resp.headers.get("Location")
            except urllib.error.HTTPError as exc:
                if exc.code not in (301, 302, 303, 307, 308):
                    break
                loc = exc.headers.get("Location") if exc.headers else None
            except Exception:
                break

        if not loc:
            break
        nxt = urljoin(current, loc.strip())
        try:
            nxt = validate_check_url(nxt)
        except AntifakeSecurityError:
            reasons.append("url_redirect_blocked_hop")
            return {
                "hops": hops,
                "final_url": current,
                "reasons": reasons,
                "blocked": True,
            }
        if nxt == current:
            break
        hops.append(nxt)
        current = nxt

    start_host = _host_of(hops[0])
    final_host = _host_of(current)
    if len(hops) > 1:
        reasons.append("url_redirect_chain")
    if start_host and final_host and start_host != final_host:
        reasons.append("url_redirect_host_mismatch")
        fuzzy = analyze_fuzzy_url(current)
        if fuzzy and not fuzzy.get("allowlisted"):
            reasons.append("brand_lookalike_redirect")
            reasons.extend(
                r for r in (fuzzy.get("reasons") or []) if r not in reasons
            )
        else:
            blob = f"{final_host} {(urlparse(current).path or '').lower()}"
            if any(tok in blob for tok in BRAND_TOKENS) and not is_allowlisted(
                final_host
            ):
                reasons.append("brand_lookalike_redirect")

    return {
        "hops": hops,
        "final_url": current,
        "reasons": reasons,
        "blocked": False,
        "confidence_boost": 0.15 if "brand_lookalike_redirect" in reasons else 0.05,
    }


def enrich_url_check_with_redirects(
    safe_url: str,
    *,
    base_reasons: List[str],
    base_confidence: float,
) -> Tuple[str, List[str], float, Optional[str]]:
    """Merge redirect probe into check_url pipeline.

    Returns (url_to_analyze, reasons, confidence, final_url_or_none).
    """
    probe = probe_redirect_chain(safe_url)
    if probe.get("blocked") and "url_redirect_blocked_hop" in (probe.get("reasons") or []):
        reasons = list(base_reasons) + list(probe.get("reasons") or [])
        # keep analyzing original; surface blocked hop
        return safe_url, reasons[:10], max(base_confidence, 0.55), None

    final_url = str(probe.get("final_url") or safe_url)
    extra = [r for r in (probe.get("reasons") or []) if r not in base_reasons]
    reasons = list(base_reasons) + extra
    conf = float(base_confidence)
    if "brand_lookalike_redirect" in extra:
        conf = max(conf, 0.82)
    elif "url_redirect_host_mismatch" in extra:
        conf = max(conf, 0.55)
    elif "url_redirect_chain" in extra:
        conf = min(1.0, conf + float(probe.get("confidence_boost") or 0.05))
    analyze = final_url if final_url != safe_url else safe_url
    return analyze, reasons[:10], conf, final_url if final_url != safe_url else None
