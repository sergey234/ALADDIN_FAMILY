"""UI статусов и карточек списка заказов."""

from __future__ import annotations

from bot.services.order_status_ui import (
    format_order_created_display,
    order_list_card_html,
    order_status_line_html,
    order_status_ui_label,
)


def test_status_labels_tz() -> None:
    assert order_status_ui_label("completed") == "🟢 Выполнен"
    assert order_status_ui_label("processing") == "🟡 В обработке"
    assert order_status_ui_label("pending_payment") == "🔵 Ожидает оплаты"
    assert order_status_ui_label("paid") == "⏳ Ожидает выдачи"
    assert order_status_ui_label("expired") == "🔴 Отменён"
    assert "Статус:</b> Выполнен" in order_status_line_html("completed")


def test_order_card_html() -> None:
    html = order_list_card_html(
        order_id=14582,
        product_title="⭐ Telegram Stars",
        rub_amount=500,
        created_at="2026-07-15 16:42:00",
        status="completed",
    )
    assert "━━━━━━━━━━━━━━" in html
    assert "⭐ Telegram Stars" in html
    assert "Заказ №14582" in html
    assert "500 ₽" in html
    assert "Статус:</b> Выполнен" in html
    assert format_order_created_display("2026-07-15T13:42:00+00:00") == "15.07.2026 16:42"


def test_hub_no_receipts_btn() -> None:
    from pathlib import Path

    kb = (Path(__file__).resolve().parents[1] / "bot" / "keyboards" / "shop_kb.py").read_text(
        encoding="utf-8"
    )
    assert 'text="📦 Мои заказы"' in kb
    assert 'text="📦 Заказы"' in kb  # списки/другие экраны
    assert "Выданные" not in kb.split("def hub_menu_kb")[1].split("def premium_dest_kb")[0]
    assert "nav:receipts" not in kb.split("def hub_menu_kb")[1].split("def premium_dest_kb")[0]
