"""Простые структурные события в лог (одна строка key=value)."""

from __future__ import annotations

import logging


def slog(logger: logging.Logger, event: str, **fields: object) -> None:
    tail = " ".join(f"{k}={v}" for k, v in sorted(fields.items(), key=lambda x: x[0]))
    logger.info("%s %s", event, tail)
