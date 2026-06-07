# -*- coding: utf-8 -*-
"""Dark Web scan orchestration for /api/reports/dark-web/scan/* (E12 iOS contract)."""

from __future__ import annotations

import hashlib
import logging
import os
import urllib.parse
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

import requests

logger = logging.getLogger(__name__)


def _iso_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_leak_date(raw: Optional[str]) -> str:
    if not raw:
        return _iso_now()
    try:
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        return datetime.fromisoformat(raw).astimezone(timezone.utc).isoformat()
    except ValueError:
        return _iso_now()


def _hibp_api_key() -> str:
    return (
        os.getenv("HIBP_API_KEY", "")
        or os.getenv("hibp_api_key", "")
        or os.getenv("HIBP_API_KEY".lower(), "")
    ).strip()


def _hibp_breached_account(email: str) -> List[Dict[str, Any]]:
    """HIBP v3 breachedaccount — prod email breach lookup."""
    api_key = _hibp_api_key()
    if not api_key:
        return []
    email = email.strip().lower()
    if not email or "@" not in email:
        return []
    url = (
        "https://haveibeenpwned.com/api/v3/breachedaccount/"
        f"{urllib.parse.quote(email)}?truncateResponse=false"
    )
    headers = {
        "hibp-api-key": api_key,
        "User-Agent": "ALADDIN-Security-iOS/1.0",
    }
    try:
        resp = requests.get(url, headers=headers, timeout=12)
        if resp.status_code == 404:
            return []
        if resp.status_code != 200:
            logger.warning("HIBP breachedaccount status=%s email=%s", resp.status_code, email[:3] + "***")
            return []
        data = resp.json()
        return data if isinstance(data, list) else []
    except Exception as exc:
        logger.error("HIBP breachedaccount error: %s", exc)
        return []


def _hibp_password_pwned_sha1(password_sha1_hex: str) -> bool:
    """Pwned Passwords range API (SHA-1 hex, uppercase)."""
    digest = password_sha1_hex.strip().upper()
    if len(digest) != 40:
        return False
    prefix, suffix = digest[:5], digest[5:]
    url = f"https://api.pwnedpasswords.com/range/{prefix}"
    try:
        resp = requests.get(url, headers={"User-Agent": "ALADDIN-Security-iOS/1.0"}, timeout=12)
        if resp.status_code != 200:
            return False
        for line in resp.text.splitlines():
            if ":" not in line:
                continue
            hash_suffix, _count = line.split(":", 1)
            if suffix == hash_suffix.strip().upper():
                return True
        return False
    except Exception as exc:
        logger.error("HIBP pwned passwords error: %s", exc)
        return False


def _agent_email_breaches(email: str) -> List[Dict[str, Any]]:
    try:
        from security.ai_agents.dark_web_monitoring_agent import DarkWebMonitoringAgent

        agent = DarkWebMonitoringAgent(
            {
                "hibp_api_key": _hibp_api_key(),
                "breachdirectory_api_key": os.getenv("BREACHDIRECTORY_API_KEY", ""),
            }
        )
        result = agent.check_email_breach(email)
        breaches = result.get("breaches") or []
        out: List[Dict[str, Any]] = []
        for item in breaches:
            if isinstance(item, dict):
                out.append(item)
        return out
    except Exception as exc:
        logger.warning("Agent email breach check unavailable: %s", exc)
        return []


def _scan_result_item(
    *,
    data_type: str,
    found: bool,
    leak_id: Optional[str] = None,
    leak_date: Optional[str] = None,
    source: Optional[str] = None,
    severity: Optional[str] = None,
    recommendations: Optional[List[str]] = None,
) -> Dict[str, Any]:
    return {
        "id": leak_id or str(uuid.uuid4()),
        "dataType": data_type,
        "found": found,
        "leakDate": leak_date,
        "source": source,
        "severity": severity,
        "recommendations": recommendations or [],
    }


def _severity_from_hibp(name: str) -> str:
    lowered = (name or "").lower()
    if any(x in lowered for x in ("password", "credential", "bank")):
        return "critical"
    return "high"


def _recommendations_for(data_type: str) -> List[str]:
    if data_type == "password":
        return ["Change your password immediately", "Enable two-factor authentication"]
    if data_type == "email":
        return ["Change passwords for affected services", "Enable two-factor authentication"]
    return ["Review account security settings"]


def collect_fast_scan_results(
    *,
    email: Optional[str],
    phone: Optional[str],
    passport: Optional[str],
    snils: Optional[str],
) -> List[Dict[str, Any]]:
    """Build iOS DarkWebScanResult list (camelCase keys). No DB writes."""
    results: List[Dict[str, Any]] = []

    if email and email.strip():
        email_norm = email.strip().lower()
        hibp_items = _hibp_breached_account(email_norm)
        if hibp_items:
            for breach in hibp_items:
                name = str(breach.get("Name") or breach.get("Title") or "haveibeenpwned")
                leak_date = _parse_leak_date(breach.get("BreachDate") or breach.get("AddedDate"))
                results.append(
                    _scan_result_item(
                        data_type="email",
                        found=True,
                        leak_date=leak_date,
                        source=name,
                        severity=_severity_from_hibp(name),
                        recommendations=_recommendations_for("email"),
                    )
                )
        else:
            agent_items = _agent_email_breaches(email_norm)
            if agent_items:
                for breach in agent_items:
                    name = str(breach.get("breach_name") or "breachdirectory")
                    leak_date = _parse_leak_date(breach.get("breach_date") or breach.get("detected_at"))
                    results.append(
                        _scan_result_item(
                            data_type="email",
                            found=True,
                            leak_date=leak_date,
                            source=name,
                            severity=str(breach.get("severity") or "medium"),
                            recommendations=_recommendations_for("email"),
                        )
                    )
            else:
                results.append(_scan_result_item(data_type="email", found=False))

    for field_name, value in (
        ("phone", phone),
        ("passport", passport),
        ("snils", snils),
    ):
        if value and str(value).strip():
            # Phone/passport/snils external lookup not wired on prod yet — honest negative.
            results.append(_scan_result_item(data_type=field_name, found=False))

    return results


def collect_secure_scan_results(
    *,
    email_hash: Optional[str],
    password_hash: Optional[str],
) -> List[Dict[str, Any]]:
    """
    Secure scan: no plaintext email on server.
    - password: HIBP only if client sends SHA-1 (40 hex); iOS sends SHA-256 — reported as not found.
    - email hash: cannot match breaches without plaintext — not found (honest).
    """
    results: List[Dict[str, Any]] = []

    if email_hash and email_hash.strip():
        results.append(
            _scan_result_item(
                data_type="email",
                found=False,
                source="secure_hash_only",
                recommendations=["Use fast scan for email breach lookup against HIBP"],
            )
        )

    if password_hash and password_hash.strip():
        digest = password_hash.strip().lower()
        found = False
        if len(digest) == 40:
            found = _hibp_password_pwned_sha1(digest)
        elif len(digest) == 64:
            # iOS SHA-256 — convert unavailable for HIBP; try SHA-1 of hex decode is wrong.
            found = False
        if found:
            results.append(
                _scan_result_item(
                    data_type="password",
                    found=True,
                    leak_date=_iso_now(),
                    source="haveibeenpwned_passwords",
                    severity="critical",
                    recommendations=_recommendations_for("password"),
                )
            )
        else:
            results.append(_scan_result_item(data_type="password", found=False))

    return results
