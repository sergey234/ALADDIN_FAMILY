# -*- coding: utf-8 -*-
"""P2-01 — Web search stub with citation URLs for companion (feature-flagged)."""

from __future__ import annotations

import re
from typing import List, Tuple
from urllib.parse import quote_plus

from .feature_flags import WEB_SEARCH_ENABLED

_SEARCH_INTENT = re.compile(
    r"(что за фильм|какой фильм|кто такой|когда вышел|новости|погода|"
    r"what is|who is|when did|news about|weather in|search for|найди|поищи)",
    re.I,
)


def maybe_companion_web_search(message: str, *, locale: str = "ru") -> Tuple[List[str], str]:
    """
    Returns (citation_urls, prompt_hint).
    MVP: deterministic placeholder citations when flag on + search intent.
    """
    if not WEB_SEARCH_ENABLED:
        return [], ""
    text = (message or "").strip()
    if len(text) < 8 or not _SEARCH_INTENT.search(text):
        return [], ""

    q = quote_plus(text[:80])
    ru = (locale or "ru").lower().startswith("ru")
    if ru:
        sources = [
            f"https://www.google.com/search?q={q}",
            "https://ru.wikipedia.org/wiki/Справка:Заглавная_страница",
        ]
        hint = (
            "[Web search: пользователь спрашивает актуальную информацию. "
            "Дай краткий ответ и упомяни, что можно уточнить у родителей. "
            "Не выдумывай факты — если не уверен, скажи честно.]\n"
        )
    else:
        sources = [
            f"https://www.google.com/search?q={q}",
            "https://en.wikipedia.org/wiki/Main_Page",
        ]
        hint = (
            "[Web search: user asks for up-to-date info. "
            "Answer briefly; cite sources in plain language. Do not invent facts.]\n"
        )
    return sources, hint
