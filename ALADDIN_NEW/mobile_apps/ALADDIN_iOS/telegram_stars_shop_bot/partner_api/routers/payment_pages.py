"""Публичные страницы редиректа после оплаты Cardlink (Success / Fail URL)."""

from __future__ import annotations

import html
import logging
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from bot.config import Settings
from bot.services.cardlink_api import verify_cardlink_payment_signature
from partner_api.deps import get_settings

router = APIRouter(tags=["payments"])
_log = logging.getLogger(__name__)


def _settings_dep(request: Request) -> Settings:
    return get_settings(request)


def _html_payment_page(
    *,
    title: str,
    headline: str,
    body: str,
    bot_url: str,
    inv_id: str | None = None,
) -> str:
    bot_href = html.escape((bot_url or "").strip() or "https://t.me/AiMonkeyStars_bot")
    inv_block = ""
    if inv_id:
        inv_block = f'<p class="muted">Заказ: <code>{html.escape(inv_id)}</code></p>'
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{html.escape(title)}</title>
  <style>
    body {{
      font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
      max-width: 28rem; margin: 3rem auto; padding: 0 1.25rem; line-height: 1.5;
      color: #111; text-align: center;
    }}
    h1 {{ font-size: 1.35rem; margin-bottom: 0.75rem; }}
    p {{ margin: 0.6rem 0; }}
    .muted {{ color: #555; font-size: 0.95rem; }}
    a.btn {{
      display: inline-block; margin-top: 1.25rem; padding: 0.75rem 1.25rem;
      background: #2481cc; color: #fff; text-decoration: none; border-radius: 10px;
      font-weight: 600;
    }}
    code {{ background: #f4f4f5; padding: 0.1rem 0.35rem; border-radius: 4px; }}
  </style>
</head>
<body>
  <h1>{html.escape(headline)}</h1>
  <p>{html.escape(body)}</p>
  {inv_block}
  <p class="muted">AIMonkey Stars · Premium · AiMonkeyVPN</p>
  <a class="btn" href="{bot_href}">Вернуться в Telegram-бот</a>
</body>
</html>"""


async def _form_fields(request: Request) -> dict[str, str]:
    if request.method == "POST":
        form = await request.form()
        return {str(k): str(v) for k, v in form.items()}
    return dict(request.query_params)


def _verify_redirect_signature(settings: Settings, fields: dict[str, str]) -> bool:
    token = (settings.cardlink_api_token or "").strip()
    if not token:
        return True
    sig = (fields.get("SignatureValue") or "").strip()
    if not sig:
        return True
    out_sum = (fields.get("OutSum") or "").strip()
    inv_id = (fields.get("InvId") or "").strip()
    if not out_sum or not inv_id:
        return False
    return verify_cardlink_payment_signature(token, out_sum=out_sum, inv_id=inv_id, signature_value=sig)


@router.api_route("/payment/success", methods=["GET", "POST"], response_class=HTMLResponse)
async def cardlink_payment_success(
    request: Request,
    settings: Annotated[Settings, Depends(_settings_dep)],
) -> HTMLResponse:
    fields = await _form_fields(request)
    inv_id = (fields.get("InvId") or "").strip() or None
    if fields and not _verify_redirect_signature(settings, fields):
        _log.warning("cardlink_success_bad_signature inv_id=%s", inv_id)
    bot_url = (settings.cardlink_return_bot_url or "https://t.me/AiMonkeyStars_bot").strip()
    page = _html_payment_page(
        title="Оплата успешна",
        headline="Оплата прошла успешно",
        body="Вернитесь в Telegram-бот — заказ будет обработан автоматически. Статус смотрите в «Мои заказы».",
        bot_url=bot_url,
        inv_id=inv_id,
    )
    return HTMLResponse(page)


@router.api_route("/payment/fail", methods=["GET", "POST"], response_class=HTMLResponse)
async def cardlink_payment_fail(
    request: Request,
    settings: Annotated[Settings, Depends(_settings_dep)],
) -> HTMLResponse:
    fields = await _form_fields(request)
    inv_id = (fields.get("InvId") or "").strip() or None
    if fields and not _verify_redirect_signature(settings, fields):
        _log.warning("cardlink_fail_bad_signature inv_id=%s", inv_id)
    bot_url = (settings.cardlink_return_bot_url or "https://t.me/AiMonkeyStars_bot").strip()
    page = _html_payment_page(
        title="Оплата не прошла",
        headline="Оплата не завершена",
        body="Попробуйте снова в боте или выберите другой способ оплаты. Если деньги списались — напишите в поддержку с номером заказа.",
        bot_url=bot_url,
        inv_id=inv_id,
    )
    return HTMLResponse(page)
