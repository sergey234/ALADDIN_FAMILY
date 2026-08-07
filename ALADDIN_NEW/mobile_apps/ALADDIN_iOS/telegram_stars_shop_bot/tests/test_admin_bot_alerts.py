from bot.services.admin_bot_alerts import format_admin_bot_alert_html


def test_format_ton_balance_ru() -> None:
    html = format_admin_bot_alert_html(
        severity="warning",
        title="iStar TON balance below threshold",
        body="balance_ton=0.0922 threshold_ton=0.1000 — auto-fulfill batch skipped",
    )
    assert "Мало TON" in html
    assert "0.0922" in html


def test_format_stuck_paid_ru() -> None:
    html = format_admin_bot_alert_html(
        severity="warning",
        title="stuck paid orders (no processing)",
        body="minutes=5 count=2 sample_ids=[73, 76]",
    )
    assert "оплачены" in html.lower()
    assert "73" in html


def test_format_completed_alert_ru() -> None:
    html = format_admin_bot_alert_html(
        severity="info",
        title="Автовыдача: заказ выдан",
        body="order_id=#77 user_id=1 товар: 100 Stars",
    )
    assert "выдан" in html.lower()


def test_format_vpn_ops_health_keeps_html_body() -> None:
    html = format_admin_bot_alert_html(
        severity="warning",
        title="VPN ops health: degraded",
        body="Статус: <b>degraded</b>\nПричины:\n• высокий swap на 149",
    )
    assert "VPN ops health: degraded" in html
    assert "<b>degraded</b>" in html
    assert "&lt;b&gt;" not in html


def test_format_vpn_ops_recovered_ru() -> None:
    html = format_admin_bot_alert_html(
        severity="info",
        title="VPN ops health: recovered",
        body="Проверка VPN снова <b>ok</b>.",
    )
    assert "восстановлено" in html.lower()
    assert "<b>ok</b>" in html
