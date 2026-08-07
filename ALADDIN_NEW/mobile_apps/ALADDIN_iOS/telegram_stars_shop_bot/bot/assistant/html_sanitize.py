"""Sanitize HTML от модели для Telegram ParseMode.HTML (R17)."""

from __future__ import annotations

import html
import re
from html.parser import HTMLParser

_ALLOWED_TAGS = frozenset({"b", "strong", "i", "em", "u", "ins", "s", "strike", "del", "code", "pre", "a", "tg-spoiler"})
_HREF_OK = re.compile(r"^(https?://|tg://|mailto:)", re.I)
_BLOCK_ATTR = re.compile(r"on\w+|javascript:", re.I)


class _Sanitizer(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._out: list[str] = []
        self._stack: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        t = tag.lower()
        if t not in _ALLOWED_TAGS:
            return
        if t == "a":
            href = ""
            for k, v in attrs:
                if (k or "").lower() == "href" and v:
                    href = v.strip()
                    break
            if not href or _BLOCK_ATTR.search(href) or not _HREF_OK.match(href):
                return
            self._out.append(f'<a href="{html.escape(href, quote=True)}">')
            self._stack.append(t)
            return
        self._out.append(f"<{t}>")
        self._stack.append(t)

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        if t not in _ALLOWED_TAGS:
            return
        if self._stack and self._stack[-1] == t:
            self._stack.pop()
            self._out.append(f"</{t}>")

    def handle_data(self, data: str) -> None:
        self._out.append(html.escape(data, quote=False))

    def handle_entityref(self, name: str) -> None:
        self._out.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        self._out.append(f"&#{name};")

    def result(self) -> str:
        while self._stack:
            t = self._stack.pop()
            self._out.append(f"</{t}>")
        return "".join(self._out)


def sanitize_telegram_html(raw: str, *, max_len: int = 3500) -> str:
    text = (raw or "").strip()
    if not text:
        return ""
    # Strip dangerous leftovers before parse.
    text = re.sub(r"(?is)<script[^>]*>.*?</script>", "", text)
    text = re.sub(r"(?is)<style[^>]*>.*?</style>", "", text)
    p = _Sanitizer()
    try:
        p.feed(text)
        p.close()
        out = p.result()
    except Exception:
        out = html.escape(text, quote=False)
    if len(out) > max_len:
        out = out[: max_len - 1] + "…"
    return out
