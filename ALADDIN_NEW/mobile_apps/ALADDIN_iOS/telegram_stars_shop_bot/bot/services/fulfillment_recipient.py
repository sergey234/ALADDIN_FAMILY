from __future__ import annotations

import re

# Как в Partner API: Telegram username без @, 4–32 символа.
_USERNAME = re.compile(r"^[a-zA-Z0-9_]{4,32}$")


def parse_fulfillment_recipient_username(user_note: str | None) -> str | None:
    """
    Получатель для выдачи Stars/Premium: ожидаем @username или username в user_note.
    Возвращает username без @ в нижнем регистре или None.
    """
    if user_note is None:
        return None
    raw = str(user_note).strip()
    if not raw:
        return None
    if raw.startswith("@"):
        raw = raw[1:].strip()
    if not raw:
        return None
    u = raw.lower()
    if not _USERNAME.match(u):
        return None
    return u
