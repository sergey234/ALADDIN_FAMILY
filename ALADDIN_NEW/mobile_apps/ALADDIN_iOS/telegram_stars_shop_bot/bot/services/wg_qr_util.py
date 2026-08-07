"""Генерация PNG QR из текста WireGuard .conf."""

from __future__ import annotations

import io


def wg_qr_png_bytes(conf_text: str) -> bytes:
    import qrcode  # optional dep: qrcode[pil] in requirements.txt

    img = qrcode.make(conf_text)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def wg_qr_filename(telegram_user_id: int) -> str:
    return f"aladdin-wg-{telegram_user_id}-qr.png"


def pay_url_qr_png_bytes(pay_url: str) -> bytes:
    """QR со ссылкой на страницу оплаты (LAVA/Ckassa). Скан → браузер → QR СБП на странице."""
    import qrcode

    img = qrcode.make((pay_url or "").strip())
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def pay_sbp_qr_filename(order_id: int) -> str:
    return f"pay-sbp-order-{order_id}.png"
