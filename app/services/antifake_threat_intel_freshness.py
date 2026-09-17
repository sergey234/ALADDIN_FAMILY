"""afhub-p2-03 — threat-intel feed freshness + alert payload.

Reads last_fetch_report.json (from antifake_fetch_external_feeds) and optional
DB source ages. Never auto-imports; ops/cron calls check_threat_intel_freshness().
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

ROOT = Path(__file__).resolve().parents[2]

# Daily cron ~03:00 — alert if last good fetch older than this
DEFAULT_MAX_AGE_HOURS = float(os.environ.get("ANTIFAKE_TI_MAX_AGE_HOURS", "36"))
DEFAULT_MIN_ACTIVE = int(os.environ.get("ANTIFAKE_PHISHING_MIN_ACTIVE", "50"))


def _feed_dir() -> Path:
    env = os.environ.get("ANTIFAKE_PHISHING_FEED_DIR", "").strip()
    if env:
        return Path(env)
    return ROOT / "data" / "antifake" / "feeds"


def _parse_iso(raw: Any) -> Optional[datetime]:
    if not raw or not isinstance(raw, str):
        return None
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def load_last_fetch_report(feed_dir: Optional[Path] = None) -> Optional[Dict[str, Any]]:
    path = (feed_dir or _feed_dir()) / "last_fetch_report.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else None
    except Exception:
        return None


def check_threat_intel_freshness(
    *,
    feed_dir: Optional[Path] = None,
    now: Optional[datetime] = None,
    max_age_hours: Optional[float] = None,
    min_active: Optional[int] = None,
    active_count: Optional[int] = None,
) -> Dict[str, Any]:
    """Return freshness status for URLHaus/OpenPhish batch feeds.

    alert=True when:
    - no report / unreadable
    - report older than max_age_hours
    - both external sources failed
    - active domain count below min (when provided)
    """
    now_utc = now or datetime.now(timezone.utc)
    if now_utc.tzinfo is None:
        now_utc = now_utc.replace(tzinfo=timezone.utc)
    max_age = float(max_age_hours if max_age_hours is not None else DEFAULT_MAX_AGE_HOURS)
    min_act = int(min_active if min_active is not None else DEFAULT_MIN_ACTIVE)
    directory = feed_dir or _feed_dir()
    report = load_last_fetch_report(directory)

    alerts: List[str] = []
    sources_out: Dict[str, Any] = {}

    if report is None:
        alerts.append("missing_last_fetch_report")
        age_hours = None
        generated_at = None
        degraded = True
        ok_sources = False
    else:
        generated_at = report.get("generated_at")
        gen_dt = _parse_iso(generated_at)
        if gen_dt is None:
            # fall back to file mtime
            path = directory / "last_fetch_report.json"
            try:
                gen_dt = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
                generated_at = gen_dt.isoformat()
            except OSError:
                gen_dt = None
                alerts.append("unreadable_generated_at")

        if gen_dt is None:
            age_hours = None
            alerts.append("stale_unknown_age")
        else:
            age_hours = (now_utc - gen_dt).total_seconds() / 3600.0
            if age_hours > max_age:
                alerts.append("fetch_report_stale")

        src = report.get("sources") if isinstance(report.get("sources"), dict) else {}
        uh = src.get("urlhaus") if isinstance(src.get("urlhaus"), dict) else {}
        op = src.get("openphish") if isinstance(src.get("openphish"), dict) else {}
        sources_out = {
            "urlhaus": {
                "ok": bool(uh.get("ok")),
                "rows": uh.get("rows"),
            },
            "openphish": {
                "ok": bool(op.get("ok")),
                "rows": op.get("rows"),
                "snapshot": bool(op.get("snapshot") or report.get("openphish_from_snapshot")),
            },
        }
        uh_ok = bool(uh.get("ok"))
        op_ok = bool(op.get("ok"))
        ok_sources = uh_ok or op_ok
        soft: List[str] = []
        if not uh_ok and not op_ok:
            alerts.append("both_external_sources_failed")
        elif not uh_ok:
            soft.append("urlhaus_failed")
        elif not op_ok:
            soft.append("openphish_failed")
        if report.get("degraded"):
            soft.append("fetch_marked_degraded")
        degraded = bool(report.get("degraded")) or (not ok_sources) or bool(soft) or bool(alerts)
        _soft_for_msg = soft

    if report is None:
        _soft_for_msg = []

    active = active_count
    if active is None:
        active = _try_active_domain_count()
    if active is not None and active < min_act:
        alerts.append("active_domains_below_min")

    alert = bool(alerts)
    ok = not alert

    # Include soft source failures in messages when alerting for other reasons,
    # or surface them as degraded-only note when ok.
    msg_alerts = list(alerts) + (_soft_for_msg if alert else [])
    if not alert and _soft_for_msg:
        msg_alerts = list(_soft_for_msg)

    return {
        "ok": ok,
        "alert": alert,
        "degraded": bool(degraded) if report is not None else True,
        "alerts": alerts,
        "warnings": _soft_for_msg if report is not None else [],
        "generated_at": generated_at,
        "age_hours": round(age_hours, 2) if isinstance(age_hours, float) else None,
        "max_age_hours": max_age,
        "min_active": min_act,
        "active_domains": active,
        "sources": sources_out,
        "feed_dir": str(directory),
        "check": "scripts/antifake_phishing_feed_gate.py",
        "message_ru": _message_ru(msg_alerts if msg_alerts else alerts, age_hours, max_age, active, min_act),
        "message_en": _message_en(msg_alerts if msg_alerts else alerts, age_hours, max_age, active, min_act),
    }


def _try_active_domain_count() -> Optional[int]:
    try:
        from sqlalchemy import text

        from app.database.database import engine

        with engine.connect() as conn:
            row = conn.execute(
                text(
                    """
                    SELECT COUNT(*) AS c
                    FROM antifake_phishing_domains
                    WHERE COALESCE(active, true) IS TRUE
                      AND (expires_at IS NULL OR expires_at > NOW())
                    """
                )
            ).mappings().first()
            return int((row or {}).get("c") or 0)
    except Exception:
        return None


def _message_ru(
    alerts: List[str],
    age_hours: Optional[float],
    max_age: float,
    active: Optional[int],
    min_act: int,
) -> str:
    if not alerts:
        age = f"{age_hours:.0f} ч" if age_hours is not None else "н/д"
        return f"Фидеры угроз свежие (возраст отчёта ~{age})."
    parts = []
    if "missing_last_fetch_report" in alerts:
        parts.append("Нет отчёта last_fetch_report.json — cron fetch не отработал.")
    if "fetch_report_stale" in alerts:
        parts.append(
            f"Отчёт fetch старше {max_age:.0f} ч (сейчас ~{age_hours:.0f} ч) — обновите URLHaus/OpenPhish."
            if age_hours is not None
            else f"Отчёт fetch старше {max_age:.0f} ч."
        )
    if "both_external_sources_failed" in alerts:
        parts.append("И URLHaus, и OpenPhish упали при последнем fetch.")
    elif "urlhaus_failed" in alerts:
        parts.append("URLHaus не обновился (OpenPhish ещё жив).")
    elif "openphish_failed" in alerts:
        parts.append("OpenPhish не обновился (URLHaus ещё жив).")
    if "active_domains_below_min" in alerts:
        parts.append(f"Активных доменов {active} < минимума {min_act}.")
    return " ".join(parts) or "Проблема свежести threat intel."


def _message_en(
    alerts: List[str],
    age_hours: Optional[float],
    max_age: float,
    active: Optional[int],
    min_act: int,
) -> str:
    if not alerts:
        age = f"{age_hours:.0f}h" if age_hours is not None else "n/a"
        return f"Threat feeds look fresh (report age ~{age})."
    parts = []
    if "missing_last_fetch_report" in alerts:
        parts.append("Missing last_fetch_report.json — fetch cron did not run.")
    if "fetch_report_stale" in alerts:
        parts.append(
            f"Fetch report older than {max_age:.0f}h (now ~{age_hours:.0f}h) — refresh URLHaus/OpenPhish."
            if age_hours is not None
            else f"Fetch report older than {max_age:.0f}h."
        )
    if "both_external_sources_failed" in alerts:
        parts.append("Both URLHaus and OpenPhish failed on last fetch.")
    elif "urlhaus_failed" in alerts:
        parts.append("URLHaus failed (OpenPhish still ok).")
    elif "openphish_failed" in alerts:
        parts.append("OpenPhish failed (URLHaus still ok).")
    if "active_domains_below_min" in alerts:
        parts.append(f"Active domains {active} < minimum {min_act}.")
    return " ".join(parts) or "Threat-intel freshness problem."
