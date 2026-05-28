"""Брендовые изображения: основной hero — файл из assets/branding (лого мартышки)."""

from __future__ import annotations

from pathlib import Path

from aiogram.types import FSInputFile

from bot.config import Settings

# telegram_stars_shop_bot/assets/branding/monkey_stars_logo.png (имя файла историческое; бренд AIMonkeyStars)
_REPO_ROOT = Path(__file__).resolve().parents[2]
BRANDING_LOGO_PATH = _REPO_ROOT / "assets" / "branding" / "monkey_stars_logo.png"


def hero_photo_input(settings: Settings) -> FSInputFile | str | None:
    """
    Картинка для онбординга / стены канала: сначала локальный лого-файл,
    иначе START_PHOTO_FILE_ID из .env (если задан).
    """
    if BRANDING_LOGO_PATH.is_file():
        return FSInputFile(BRANDING_LOGO_PATH)
    fid = (settings.start_photo_file_id or "").strip()
    return fid if fid else None
