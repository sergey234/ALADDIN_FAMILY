from __future__ import annotations

from partner_api.rate_limit_middleware import _webhook_alert_status


def test_webhook_alert_status_skips_expected_401() -> None:
    assert _webhook_alert_status(401) is False


def test_webhook_alert_status_alerts_other_client_errors() -> None:
    assert _webhook_alert_status(403) is True
    assert _webhook_alert_status(422) is True


def test_webhook_alert_status_alerts_server_errors() -> None:
    assert _webhook_alert_status(500) is True
