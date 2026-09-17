"""T3-06 — confidence calibration metrics on golden dataset (rule-engine / offline SFM)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List
from unittest.mock import patch

from data.antifake.golden_dataset import (
    golden_sms_en,
    golden_sms_ru,
    golden_text_en,
    golden_text_ru,
    golden_urls,
)

TEXT_SCAM_MIN_CONF = 0.65
TEXT_SMS_SCAM_MIN_CONF = 0.65
URL_SCAM_MIN_CONF = 0.55
REAL_MAX_CONF = 0.55

_VERDICT_RANK = {
    "likely_fake": 3,
    "uncertain": 2,
    "insufficient_data": 1,
    "likely_real": 0,
}


@dataclass
class CalibrationBucket:
    name: str
    total: int = 0
    passed: int = 0
    failures: List[str] = field(default_factory=list)

    @property
    def rate(self) -> float:
        return (self.passed / self.total) if self.total else 1.0


@dataclass
class CalibrationReport:
    buckets: Dict[str, CalibrationBucket]
    generated_at: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "generated_at": self.generated_at,
            "thresholds": {
                "text_scam_min_confidence": TEXT_SCAM_MIN_CONF,
                "text_sms_scam_min_confidence": TEXT_SMS_SCAM_MIN_CONF,
                "url_scam_min_confidence": URL_SCAM_MIN_CONF,
                "real_max_confidence": REAL_MAX_CONF,
            },
            "buckets": {
                name: {
                    "total": b.total,
                    "passed": b.passed,
                    "rate": round(b.rate, 4),
                    "failures": b.failures[:20],
                }
                for name, b in self.buckets.items()
            },
            "all_passed": all(b.passed == b.total for b in self.buckets.values()),
        }


def _conf(payload: Dict[str, Any]) -> float:
    raw = payload.get("confidence")
    if raw is None:
        raw = payload.get("fake_risk")
    try:
        return float(raw or 0.0)
    except (TypeError, ValueError):
        return 0.0


def _record(bucket: CalibrationBucket, ok: bool, detail: str) -> None:
    bucket.total += 1
    if ok:
        bucket.passed += 1
    elif len(bucket.failures) < 30:
        bucket.failures.append(detail)


def run_calibration(*, mock_sfm_offline: bool = True) -> CalibrationReport:
    from datetime import datetime, timezone

    from app.services.antifake_service import check_text, check_url

    buckets = {
        "text_ru_scam": CalibrationBucket("text_ru_scam"),
        "text_ru_real": CalibrationBucket("text_ru_real"),
        "text_en_scam": CalibrationBucket("text_en_scam"),
        "text_en_real": CalibrationBucket("text_en_real"),
        "text_sms_ru_scam": CalibrationBucket("text_sms_ru_scam"),
        "text_sms_en_scam": CalibrationBucket("text_sms_en_scam"),
        "url_fake": CalibrationBucket("url_fake"),
        "url_real": CalibrationBucket("url_real"),
    }

    def _run_text(cases, scam_key: str, real_key: str, *, mode: str = "news") -> None:
        for text, expected in cases:
            out = check_text(text, mode=mode)
            conf = _conf(out)
            verdict = str(out.get("verdict") or "")
            min_conf = TEXT_SMS_SCAM_MIN_CONF if mode == "sms" else TEXT_SCAM_MIN_CONF
            if expected == "likely_fake":
                ok = verdict == "likely_fake" and conf >= min_conf
                _record(
                    buckets[scam_key],
                    ok,
                    f"conf={conf:.3f} verdict={verdict} mode={mode} text={text[:60]}",
                )
            else:
                ok = verdict in ("likely_real", "uncertain", "insufficient_data") and conf <= REAL_MAX_CONF
                _record(
                    buckets[real_key],
                    ok,
                    f"conf={conf:.3f} verdict={verdict} mode={mode} text={text[:60]}",
                )

    def _run_urls() -> None:
        for url, expected in golden_urls():
            out = check_url(url)
            conf = _conf(out)
            verdict = str(out.get("verdict") or "")
            if expected == "likely_fake":
                # RH-B03: verdict primary; confidence soft floor for heuristics/fuzzy
                ok = verdict == "likely_fake" and conf >= URL_SCAM_MIN_CONF
                _record(buckets["url_fake"], ok, f"conf={conf:.3f} verdict={verdict} url={url}")
            else:
                ok = verdict in ("likely_real", "uncertain", "insufficient_data") and verdict != "likely_fake"
                _record(buckets["url_real"], ok, f"conf={conf:.3f} verdict={verdict} url={url}")

    patches = [
        patch(
            "app.services.antifake_phishing_domains_store.lookup_url_domain",
            return_value=None,
        ),
        patch(
            "app.services.antifake_phishing_domains_store.lookup_rkn_blocked",
            return_value=None,
        ),
        patch("app.services.antifake_security.validate_check_url", side_effect=lambda u: u),
    ]
    if mock_sfm_offline:
        patches.insert(
            0,
            patch(
                "app.services.antifake_service._sfm_execute",
                return_value={"success": False, "error": "offline"},
            ),
        )

    from contextlib import ExitStack

    with ExitStack() as stack:
        for p in patches:
            stack.enter_context(p)
        _run_text(golden_text_ru(), "text_ru_scam", "text_ru_real")
        _run_text(golden_text_en(), "text_en_scam", "text_en_real")
        for text, expected in golden_sms_ru():
            out = check_text(text, mode="sms")
            conf = _conf(out)
            verdict = str(out.get("verdict") or "")
            ok = expected == "likely_fake" and verdict == "likely_fake" and conf >= TEXT_SMS_SCAM_MIN_CONF
            _record(
                buckets["text_sms_ru_scam"],
                ok,
                f"conf={conf:.3f} verdict={verdict} text={text[:60]}",
            )
        for text, expected in golden_sms_en():
            out = check_text(text, mode="sms")
            conf = _conf(out)
            verdict = str(out.get("verdict") or "")
            ok = expected == "likely_fake" and verdict == "likely_fake" and conf >= TEXT_SMS_SCAM_MIN_CONF
            _record(
                buckets["text_sms_en_scam"],
                ok,
                f"conf={conf:.3f} verdict={verdict} text={text[:60]}",
            )
        _run_urls()

    return CalibrationReport(
        buckets=buckets,
        generated_at=datetime.now(timezone.utc).isoformat(),
    )


def aggregate_verdict(verdicts: List[str]) -> str:
    if not verdicts:
        return "insufficient_data"
    best = max(verdicts, key=lambda v: _VERDICT_RANK.get(v, 0))
    return best
