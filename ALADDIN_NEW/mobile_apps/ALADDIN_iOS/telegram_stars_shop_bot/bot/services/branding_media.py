"""Брендовые изображения: hero — file_id (кэш/.env), иначе локальный файл."""

from __future__ import annotations

from pathlib import Path

from aiogram.types import FSInputFile, Message

from bot.config import Settings

# telegram_stars_shop_bot/assets/branding/monkey.jpg — hero для онбординга, канала, капчи
_REPO_ROOT = Path(__file__).resolve().parents[2]
_BRANDING_DIR = _REPO_ROOT / "assets" / "branding"
BRANDING_LOGO_PATH = _BRANDING_DIR / "monkey.jpg"
BRANDING_LOGO_LEGACY_PATH = _BRANDING_DIR / "monkey_stars_logo.png"

# Process-wide cache after first successful upload (avoids re-uploading ~90KB every /start).
_cached_hero_file_id: str = ""


def _resolve_branding_logo_path() -> Path | None:
    if BRANDING_LOGO_PATH.is_file():
        return BRANDING_LOGO_PATH
    if BRANDING_LOGO_LEGACY_PATH.is_file():
        return BRANDING_LOGO_LEGACY_PATH
    return None


def remember_hero_file_id(file_id: str) -> None:
    """Запомнить file_id после успешной отправки фото (следующий /start без upload)."""
    global _cached_hero_file_id
    fid = (file_id or "").strip()
    if fid:
        _cached_hero_file_id = fid


def remember_hero_file_id_from_message(msg: Message | None) -> None:
    if msg is None or not msg.photo:
        return
    remember_hero_file_id(msg.photo[-1].file_id)


def clear_hero_file_id_cache_for_tests() -> None:
    global _cached_hero_file_id
    _cached_hero_file_id = ""


def hero_photo_input(settings: Settings) -> FSInputFile | str | None:
    """
    Картинка для онбординга / стены канала / капчи:
    1) START_PHOTO_FILE_ID из .env
    2) process cache после первой отправки
    3) локальный лого-файл (upload)
    """
    env_fid = (settings.start_photo_file_id or "").strip()
    if env_fid:
        return env_fid
    if _cached_hero_file_id:
        return _cached_hero_file_id
    logo = _resolve_branding_logo_path()
    if logo is not None:
        return FSInputFile(logo)
    return None
