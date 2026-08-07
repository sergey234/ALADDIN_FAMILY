from __future__ import annotations

from pathlib import Path

from bot.services.ops_watchdog import _count_recent_errors, _count_telegram_timeouts


def test_count_recent_errors_ignores_message_not_modified(tmp_path: Path) -> None:
    log = tmp_path / "bot.log"
    log.write_text(
        "\n".join(
            [
                "INFO:ok",
                "ERROR:aiogram.event:Cause exception while process update id=1",
                "TelegramBadRequest: message is not modified: specified new message content",
                "Traceback (most recent call last):",
                "ERROR:real failure something broke",
            ]
        ),
        encoding="utf-8",
    )
    assert _count_recent_errors(log, 50) == 1


def test_count_telegram_timeouts(tmp_path: Path) -> None:
    log = tmp_path / "bot.log"
    log.write_text(
        "\n".join(
            [
                "INFO:ok",
                "ERROR: TelegramNetworkError: HTTP Client says - Request timeout error",
                "WARNING: Request timeout while waiting",
                "INFO: Update id=1 is handled",
            ]
        ),
        encoding="utf-8",
    )
    assert _count_telegram_timeouts(log, 50) == 2
