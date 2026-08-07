from __future__ import annotations

import html as _html


def esc(s: str | int | float | None) -> str:
    if s is None:
        return ""
    return _html.escape(str(s), quote=True)
