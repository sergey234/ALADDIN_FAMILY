from __future__ import annotations

from bot.config import load_settings
from bot.services.ops_watchdog import _evaluate_kpi_thresholds


def _base_settings(monkeypatch):
    monkeypatch.setenv("BOT_TOKEN", "1:watchdog")
    monkeypatch.setenv("USD_RUB_RATE", "100")
    monkeypatch.setenv("OPS_ALERT_CAC_MAX_RUB", "1500")
    return load_settings()


def test_evaluate_kpi_thresholds_detects_all_problems(monkeypatch) -> None:
    settings = _base_settings(monkeypatch)
    checks = _evaluate_kpi_thresholds(
        settings=settings,
        days=7,
        payment={"funnel_created_orders": 120, "funnel_paid_rate_pct": 70.0},
        webhook={"webhook_total": 80, "webhook_success_rate_pct": 90.0, "webhook_latency_p95_sec": 120.0},
        retention={"retention_cohort_size": 120, "retention_d7_pct": 4.5},
        acquisition={"acq_paid_users": 22, "acq_cac_rub": 2400.0},
    )
    assert checks["kpi_payment_success_rate"][0] is True
    assert checks["kpi_webhook_sla"][0] is True
    assert checks["kpi_retention_d7"][0] is True
    assert checks["kpi_cac"][0] is True


def test_evaluate_kpi_thresholds_ignores_small_samples(monkeypatch) -> None:
    settings = _base_settings(monkeypatch)
    checks = _evaluate_kpi_thresholds(
        settings=settings,
        days=7,
        payment={"funnel_created_orders": 5, "funnel_paid_rate_pct": 10.0},
        webhook={"webhook_total": 3, "webhook_success_rate_pct": 20.0, "webhook_latency_p95_sec": 999.0},
        retention={"retention_cohort_size": 4, "retention_d7_pct": 0.0},
        acquisition={"acq_paid_users": 1, "acq_cac_rub": 99999.0},
    )
    assert checks["kpi_payment_success_rate"][0] is False
    assert checks["kpi_webhook_sla"][0] is False
    assert checks["kpi_retention_d7"][0] is False
    assert checks["kpi_cac"][0] is False
