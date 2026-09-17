"""T3-04 — public antifake capabilities / model card (no auth, no PII)."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict

from app.services.antifake_audio_ensemble import AUDIO_MODEL_CARD
from app.services.antifake_calibration import REAL_MAX_CONF, TEXT_SCAM_MIN_CONF, URL_SCAM_MIN_CONF
from app.services.antifake_service import (
    AUDIO_AGENT,
    DOCUMENT_AGENT,
    FORBIDDEN_SOURCES,
    MODEL_VERSION,
    SLA_MS,
    TEXT_AGENT,
    URL_AGENTS,
    VIDEO_AGENTS,
)
from app.services.antifake_call_directory_store import MIN_RU_SEED_COUNT
from app.services.antifake_phishing_domains_store import MIN_PHISHING_DOMAIN_COUNT
from app.services.antifake_text_ensemble import TEXT_MODEL_CARD
from app.services.antifake_video_ensemble import VIDEO_MODEL_CARD


def _dark_web_capabilities() -> Dict[str, Any]:
    try:
        from security.api.dark_web_scan_service import hibp_status

        return hibp_status()
    except Exception:
        return {
            "email_breaches": {"configured": False, "env": "HIBP_API_KEY"},
            "password_pwned": {
                "configured": True,
                "protocol": "sha1_k_anonymity",
                "api_key_required": False,
            },
        }


def _threat_intel_freshness_snapshot() -> Dict[str, Any]:
    """afhub-p2-03 — public freshness slice (no secrets)."""
    try:
        from app.services.antifake_threat_intel_freshness import check_threat_intel_freshness

        snap = check_threat_intel_freshness()
        return {
            "ok": bool(snap.get("ok")),
            "alert": bool(snap.get("alert")),
            "age_hours": snap.get("age_hours"),
            "max_age_hours": snap.get("max_age_hours"),
            "active_domains": snap.get("active_domains"),
            "sources": snap.get("sources") or {},
            "check": snap.get("check"),
        }
    except Exception as exc:
        return {"ok": False, "alert": True, "error": type(exc).__name__}


def public_capabilities_payload() -> Dict[str, Any]:
    return {
        "model_version": MODEL_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pipelines": {
            "text": {
                "endpoint": "POST /api/antifake/check/text",
                "source": "ensemble_text",
                "sla_ms": SLA_MS["text"],
                "model_card": TEXT_MODEL_CARD,
            },
            "url": {
                "endpoint": "POST /api/antifake/check/url",
                "source": "threat_feed|real_agent|rule_engine",
                "sla_ms": SLA_MS["url"],
                "agents": list(URL_AGENTS),
                "model_card": {
                    "ensemble_version": "antifake_url_v1",
                    "channels": {
                        "feed": {"agent": "phishing_domain_feed", "tier": "threat_intel"},
                        "fuzzy": {"agent": "url_fuzzy", "tier": "heuristic"},
                        "phishing_agent": {
                            "agent": "phishing_protection_agent",
                            "tier": "real_agent",
                            "role": "secondary",
                        },
                        "rules": {"agent": "heuristic_url", "tier": "heuristic"},
                    },
                    "sfm_stub": False,
                },
                "feed": {
                    "bundled_csv": "data/antifake/phishing_domains_ru_v1.csv",
                    "cron": "scripts/antifake_cron_import_phishing_domains.py",
                    "schedule": "daily 03:15 (crontab aladdin-antifake-phishing-import)",
                    "min_active_domains": MIN_PHISHING_DOMAIN_COUNT,
                    "optional_feed_dir_env": "ANTIFAKE_PHISHING_FEED_DIR",
                    "external_fetch": "scripts/antifake_fetch_external_feeds.py",
                    "external_sources": ["urlhaus", "openphish"],
                },
            },
            "audio": {
                "endpoint": "POST /api/antifake/check/audio",
                "source": "ensemble_audio",
                "sla_ms": SLA_MS["audio"],
                "model_card": AUDIO_MODEL_CARD,
            },
            "video": {
                "endpoint": "POST /api/antifake/check/video",
                "source": "ensemble_video",
                "sla_ms": SLA_MS["video"],
                "model_card": VIDEO_MODEL_CARD,
            },
            "call": {
                "endpoint": "POST /api/antifake/call/analyze",
                "source": "ensemble_audio",
                "sla_ms": SLA_MS["call"],
                "model_card": {
                    **AUDIO_MODEL_CARD,
                    "note": "call extends audio ensemble with spoof metadata channel",
                },
            },
            "document": {
                "endpoint": "POST /api/antifake/check/document",
                "source": "real_agent|rule_engine",
                "sla_ms": SLA_MS["document"],
                "agent": DOCUMENT_AGENT,
                "model_card": {
                    "ensemble_version": "antifake_document_v1",
                    "channels": {
                        "local": {
                            "agent": "fake_documents_local",
                            "tier": "local_ml",
                            "primary": True,
                            "note": "bytes→temp→OpenCV / PDF heuristics on worker",
                        },
                        "sfm": {
                            "agent": DOCUMENT_AGENT,
                            "tier": "mirror_optional",
                            "accepts": ["image_path", "file_bytes_b64"],
                        },
                        "provenance": {"agent": "document_provenance", "tier": "metadata"},
                    },
                },
            },
        },
        "threat_intel": {
            "mode": "hybrid_batch_online",
            "sources": ["ru_v1_seed", "urlhaus", "openphish", "ru_expand"],
            "dedupe": "source_priority (qa>ru_v1>openphish>urlhaus>rkn)",
            "fuzzy": True,
            "allowlist": True,
            "rkn_imported": os.environ.get("ANTIFAKE_RKN_IMPORT_ENABLED", "0").strip()
            in ("1", "true", "yes", "on"),
            "rkn_legal_gate": "docs/ANTIFAKE_RKN_LEGAL_GATE.md",
            "gis_antifrod": False,
            "honest_copy": [
                "Проверяем с базами угроз и открытыми источниками",
                "Сверяем номера с открытыми репутационными базами",
            ],
            "freshness": _threat_intel_freshness_snapshot(),
        },
        "dark_web": _dark_web_capabilities(),
        "agents": {
            "text": TEXT_AGENT,
            "audio": AUDIO_AGENT,
            "video": list(VIDEO_AGENTS),
            "document": DOCUMENT_AGENT,
            "url": list(URL_AGENTS),
        },
        "calibration": {
            "text_scam_min_confidence": TEXT_SCAM_MIN_CONF,
            "url_scam_min_confidence": URL_SCAM_MIN_CONF,
            "real_max_confidence": REAL_MAX_CONF,
            "golden_set": "data/antifake/golden_dataset.py",
        },
        "policy": {
            "forbidden_sources": sorted(FORBIDDEN_SOURCES),
            "probe_never_likely_fake": ["audio", "video"],
            "no_background_sms_scan": True,
            "no_live_call_intercept": True,
        },
        "call_directory": {
            "endpoint": "GET /api/antifake/call-directory",
            "min_active_numbers": MIN_RU_SEED_COUNT,
            "feed": {
                "bundled_csv": "data/antifake/scam_numbers_ru_v1.csv",
                "cron": "scripts/antifake_cron_import_scam_numbers.py",
                "schedule": "daily 03:00 (crontab aladdin-antifake-scam-import)",
                "optional_feed_dir_env": "ANTIFAKE_SCAM_FEED_DIR",
                "external_fetch": "scripts/antifake_fetch_scam_feeds.py",
                "external_sources": ["ru_seed_expand", "call_analyze", "user_report"],
            },
        },
        "ops": {
            "drift_alert": {
                "metric": "uncertain_rate",
                "window_hours": int(os.environ.get("ANTIFAKE_DRIFT_WINDOW_HOURS", "24")),
                "threshold_pct": float(os.environ.get("ANTIFAKE_DRIFT_UNCERTAIN_PCT", "45")),
                "min_sample": int(os.environ.get("ANTIFAKE_DRIFT_MIN_SAMPLE", "50")),
                "check": "scripts/antifake_ops_alerts.py --check-drift",
            },
            "scam_feed_import": {
                "check": "scripts/antifake_cron_import_scam_numbers.py",
                "min_active_numbers": MIN_RU_SEED_COUNT,
            },
            "phishing_feed_import": {
                "check": "scripts/antifake_cron_import_phishing_domains.py",
                "min_active_domains": MIN_PHISHING_DOMAIN_COUNT,
                "freshness_gate": "scripts/antifake_phishing_feed_gate.py",
                "max_age_hours_env": "ANTIFAKE_TI_MAX_AGE_HOURS",
            },
            "scam_feed_push": {
                "event": "scam_feed_updated",
                "cooldown_hours": int(os.environ.get("ANTIFAKE_SCAM_FEED_PUSH_COOLDOWN_SEC", str(24 * 3600))) // 3600,
            },
            "moderation_sla": {
                "hours": int(os.environ.get("ANTIFAKE_MODERATION_SLA_HOURS", "48")),
                "check": "scripts/antifake_ops_alerts.py --check-moderation-sla",
            },
            "verdict_feedback": {
                "endpoint": "POST /api/antifake/feedback",
                "metrics": "GET /api/antifake/feedback/metrics",
                "lexicon_queue": "GET /api/antifake/feedback/lexicon-queue",
                "rule_tweaks": "data/antifake/rule_tweaks.json",
                "lexicon_review_queue": "data/antifake/lexicon_review_queue.jsonl",
                "note": "was_scam → review queue only; never auto-writes live lexicon",
            },
        },
        # RH-AG01: honest agent inventory (wire / secondary / off)
        "agent_policy": {
            "fake_news_detection_agent": {
                "role": "soft",
                "status": "wired",
                "note": "SMS: rules primary; model soft signal",
            },
            "phishing_protection_agent": {
                "role": "secondary",
                "status": "wired",
                "note": "After feed+fuzzy; allowlist-safe",
            },
            "fake_documents_agent": {
                "role": "primary_doc",
                "status": "wired",
                "note": "analyze_document_bytes primary; SFM accepts file_bytes_b64",
            },
            "audio_deepfake_local": {
                "role": "primary_audio",
                "status": "wired",
                "tier": "local_ml",
            },
            "video_deepfake_local": {
                "role": "primary_video",
                "status": "wired",
                "tier": "local_ml",
                "note": "Metadata/container; DeepfakeProtectionSystem OFF",
            },
            "video_onnx_local": {
                "role": "optional_video_nn",
                "status": "flagged",
                "tier": "local_ml",
                "enabled": os.environ.get("ANTIFAKE_VIDEO_ONNX", "0").strip()
                in ("1", "true", "yes", "on"),
                "flag": "ANTIFAKE_VIDEO_ONNX",
                "model_path_env": "ANTIFAKE_VIDEO_ONNX_MODEL_PATH",
                "note": "AG07 light ONNX CPU; heuristic frames if model missing",
            },
            "DeepfakeProtectionSystem": {
                "role": "off",
                "status": "hard_off",
                "note": "Stubs with false confidence; replaced by video_onnx_local (AG07)",
            },
        },
        "sfm_inventory": _sfm_inventory_payload(),
    }


def _sfm_inventory_payload() -> Dict[str, Any]:
    try:
        from app.services.antifake_sfm_inventory import inventory_summary

        return inventory_summary()
    except Exception:
        return {"total": 0, "rows": []}
