"""Публичные страницы политики и соглашения (тексты из каталога legal/)."""

from __future__ import annotations

import html
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

_REPO_ROOT = Path(__file__).resolve().parents[2]
_PRIVACY_PATH = _REPO_ROOT / "legal" / "privacy_policy_ru.txt"
_TERMS_PATH = _REPO_ROOT / "legal" / "terms_of_service_ru.txt"
_OFFER_PATH = _REPO_ROOT / "legal" / "public_offer_ru.txt"
_REFUND_PATH = _REPO_ROOT / "legal" / "refund_policy_ru.txt"

_NEWS_CHANNEL_URL = "https://t.me/+xwj4zZo4bNphZjVi"
_SHOP_BOT_URL = "https://t.me/AiMonkeyStars_bot"

router = APIRouter(tags=["legal"])


def _html_page(title: str, body_text: str) -> str:
    esc = html.escape(body_text.strip())
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
      max-width: 42rem; margin: 2rem auto; padding: 0 1rem; line-height: 1.55; color: #111; }}
    pre {{ white-space: pre-wrap; font-family: inherit; font-size: 15px; margin: 0; }}
  </style>
</head>
<body>
  <pre>{esc}</pre>
</body>
</html>"""


def _read_text(path: Path) -> str:
    if not path.is_file():
        return "Документ временно недоступен."
    return path.read_text(encoding="utf-8")


@router.get("/legal/privacy", response_class=HTMLResponse)
async def privacy_policy_page() -> HTMLResponse:
    body = _read_text(_PRIVACY_PATH)
    return HTMLResponse(_html_page("Политика конфиденциальности", body))


@router.get("/legal/terms", response_class=HTMLResponse)
async def terms_of_service_page() -> HTMLResponse:
    body = _read_text(_TERMS_PATH)
    return HTMLResponse(_html_page("Пользовательское соглашение", body))


@router.get("/legal/offer", response_class=HTMLResponse)
async def public_offer_page() -> HTMLResponse:
    body = _read_text(_OFFER_PATH)
    return HTMLResponse(_html_page("Публичная оферта", body))


@router.get("/legal/refund", response_class=HTMLResponse)
async def refund_policy_page() -> HTMLResponse:
    body = _read_text(_REFUND_PATH)
    # Явная HTML-таблица сроков (шаблон Lava) + полный текст.
    table = """
  <h2>Сроки</h2>
  <table>
    <tr><th>Пункт</th><th>Условие</th></tr>
    <tr><td>После выдачи («выдан»)</td><td><strong>Возврату не подлежат</strong></td></tr>
    <tr><td>Оказание услуги</td><td>Фактически <strong>от 5 минут до 24 часов</strong>; максимум — <strong>3 календарных дня</strong> с момента оплаты</td></tr>
    <tr><td>Подача заявки на возврат</td><td><strong>14 календарных дней</strong> после просрочки 3-дневного срока, если заказ не «выдан»</td></tr>
    <tr><td>Рассмотрение</td><td>До <strong>10 рабочих дней</strong></td></tr>
    <tr><td>Возврат денег</td><td>До <strong>14 рабочих дней</strong> после одобрения, <strong>на те же реквизиты, в полном объёме</strong></td></tr>
  </table>
  <p>Заявка: бот → «Поддержка» → «Написать оператору» (тикет видит только администрация).</p>
"""
    esc_body = html.escape(body.strip())
    page = f"""<!DOCTYPE html>
<html lang="ru">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>Политика возвратов</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
      max-width: 42rem; margin: 2rem auto; padding: 0 1rem; line-height: 1.55; color: #111; }}
    pre {{ white-space: pre-wrap; font-family: inherit; font-size: 15px; margin: 1rem 0 0; }}
    table {{ width: 100%; border-collapse: collapse; margin: 1rem 0; font-size: 0.95rem; }}
    th, td {{ border: 1px solid #ddd; padding: 0.5rem 0.65rem; text-align: left; vertical-align: top; }}
    th {{ background: #f4f4f5; }}
    h1 {{ font-size: 1.45rem; }}
    h2 {{ font-size: 1.1rem; margin-top: 1.25rem; }}
  </style>
</head>
<body>
  <h1>Политика возвратов</h1>
  {table}
  <h2>Полный текст</h2>
  <pre>{esc_body}</pre>
</body>
</html>"""
    return HTMLResponse(page)


@router.get("/legal/news", response_class=HTMLResponse)
async def news_channel_page() -> HTMLResponse:
    body = f"""НОВОСТНОЙ КАНАЛ МАГАЗИНА AiMonkey Stars | Premium | AiMonkeyVPN

Официальный Telegram-канал магазина цифровых товаров и услуг:
{_NEWS_CHANNEL_URL}

В канале публикуются:
- новости магазина и обновления ассортимента;
- изменения тарифов и условий;
- технические уведомления и статус работы сервисов;
- акции и специальные предложения.

Telegram-бот для покупок: {_SHOP_BOT_URL}

Публичная оферта: /v1/legal/offer
Политика возвратов: /v1/legal/refund
Политика конфиденциальности: /v1/legal/privacy

© 2026 AiMonkeyStars."""
    return HTMLResponse(_html_page("Новостной канал", body))
