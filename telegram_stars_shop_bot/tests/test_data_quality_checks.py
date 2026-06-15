from __future__ import annotations

from bot.config import load_settings
from bot.services.data_quality_checks import _evaluate_thresholds


def test_data_quality_thresholds_detect_problem(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:dq")
    monkeypatch.setenv("USD_RUB_RATE", "90")
    s = load_settings()
    checks = _evaluate_thresholds(
        s,
        {
            "missing_kind": 3,
            "missing_profit": 2,
            "events_v2_pct": 75.0,
            "paid_unknown_pct": 50.0,
        },
    )
    assert checks["orders_missing_kind"][0] is True
    assert checks["orders_missing_profit_snapshot"][0] is True
    assert checks["analytics_schema_v2"][0] is True
    assert checks["unattributed_paid_users"][0] is True


def test_data_quality_thresholds_ok(monkeypatch) -> None:
    monkeypatch.setenv("BOT_TOKEN", "9:dq2")
    monkeypatch.setenv("USD_RUB_RATE", "90")
    s = load_settings()
    checks = _evaluate_thresholds(
        s,
        {
            "missing_kind": 0,
            "missing_profit": 0,
            "events_v2_pct": 99.0,
            "paid_unknown_pct": 5.0,
        },
    )
    assert checks["orders_missing_kind"][0] is False
    assert checks["orders_missing_profit_snapshot"][0] is False
    assert checks["analytics_schema_v2"][0] is False
    assert checks["unattributed_paid_users"][0] is False
