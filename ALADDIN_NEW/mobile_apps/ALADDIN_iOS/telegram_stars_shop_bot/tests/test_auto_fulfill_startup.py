from __future__ import annotations

import pytest

from bot.config import Settings
from bot.services.auto_fulfill_startup import log_auto_fulfill_startup_warnings


def _s(**kwargs: object) -> Settings:
    base: dict[str, object] = dict(
        BOT_TOKEN="9:x",
        ADMIN_IDS="1",
        API_KEY_PEPPER="k" * 32,
    )
    base.update(kwargs)
    return Settings(**base)  # type: ignore[arg-type]


def test_startup_warning_when_auto_without_istar_key(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level("WARNING")
    log_auto_fulfill_startup_warnings(
        _s(AUTO_FULFILL_ENABLED=True, AUTO_FULFILL_STARS_ENABLED=True, ISTAR_API_KEY="")
    )
    assert any("ISTAR_API_KEY" in r.message for r in caplog.records)


def test_no_warning_when_auto_disabled(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level("WARNING")
    log_auto_fulfill_startup_warnings(_s(AUTO_FULFILL_ENABLED=False))
    assert not [r for r in caplog.records if "AUTO_FULFILL" in r.message]
