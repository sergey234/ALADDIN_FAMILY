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
