"""VPN медиа: видео-инструкция App Store (регион для Happ) + иконка приложения."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from aiogram.types import FSInputFile, InlineKeyboardMarkup, Message

from bot.config import Settings

_log = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[2]
HAPP_REGION_VIDEO_FILENAME = "happ_appstore_region_guide.mp4"
HAPP_REGION_VIDEO_PATH = _REPO_ROOT / "assets" / "vpn" / HAPP_REGION_VIDEO_FILENAME
HAPP_APP_ICON_FILENAME = "happ_app_icon.png"
HAPP_APP_ICON_PATH = _REPO_ROOT / "assets" / "vpn" / HAPP_APP_ICON_FILENAME

# Persisted Telegram file_id (избегаем повторной загрузки 3MB → timeout).
_FILE_ID_CACHE_CANDIDATES = (
    Path("/opt/aladdin-telegram-shop-bot/data/happ_media_file_ids.json"),
    _REPO_ROOT / "data" / "happ_media_file_ids.json",
)


def _cache_path() -> Path:
    for p in _FILE_ID_CACHE_CANDIDATES:
        try:
            p.parent.mkdir(parents=True, exist_ok=True)
            return p
        except OSError:
            continue
    return _FILE_ID_CACHE_CANDIDATES[-1]


def _load_file_id_cache() -> dict[str, str]:
    path = _cache_path()
    try:
        if not path.is_file():
            return {}
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            return {}
        out: dict[str, str] = {}
        for k, v in raw.items():
            if isinstance(k, str) and isinstance(v, str) and v.strip():
                out[k] = v.strip()
        return out
    except Exception:
        _log.warning("happ_media_file_id_cache_read_failed path=%s", path, exc_info=True)
        return {}


def _save_file_id_cache(updates: dict[str, str]) -> None:
    if not updates:
        return
    path = _cache_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        cur = _load_file_id_cache()
        cur.update({k: v.strip() for k, v in updates.items() if (v or "").strip()})
        path.write_text(json.dumps(cur, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        _log.info("happ_media_file_id_cache_saved path=%s keys=%s", path, sorted(updates))
    except Exception:
        _log.warning("happ_media_file_id_cache_write_failed path=%s", path, exc_info=True)


def happ_region_video_input(settings: Settings) -> FSInputFile | str | None:
    """Telegram file_id (env → cache) или локальный mp4."""
    fid = (getattr(settings, "vpn_happ_region_video_file_id", None) or "").strip()
    if fid:
        return fid
    cached = _load_file_id_cache().get("video")
    if cached:
        return cached
    if HAPP_REGION_VIDEO_PATH.is_file():
        return FSInputFile(HAPP_REGION_VIDEO_PATH)
    return None


def happ_app_icon_input() -> FSInputFile | str | None:
    cached = _load_file_id_cache().get("icon")
    if cached:
        return cached
    if HAPP_APP_ICON_PATH.is_file():
        return FSInputFile(HAPP_APP_ICON_PATH)
    return None


def _extract_file_ids(messages: list[Message] | Message | None) -> dict[str, str]:
    out: dict[str, str] = {}
    items: list[Any]
    if messages is None:
        return out
    if isinstance(messages, Message):
        items = [messages]
    else:
        items = list(messages)
    for msg in items:
        if getattr(msg, "photo", None):
            fid = msg.photo[-1].file_id
            if fid:
                out["icon"] = fid
        video = getattr(msg, "video", None)
        if video is not None and getattr(video, "file_id", None):
            out["video"] = video.file_id
    return out


def _maybe_cache_ids(sent: Message | list[Message] | None, *, uploaded_from_disk: bool) -> None:
    if not uploaded_from_disk or sent is None:
        return
    ids = _extract_file_ids(sent)
    if ids:
        _save_file_id_cache(ids)


async def send_happ_region_video(
    message: Message,
    settings: Settings,
    *,
    caption_html: str | None = None,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> bool:
    """
    Один экран: иконка + полный текст шагов + кнопки, затем видео.

    Media group в Telegram не поддерживает inline-кнопки — поэтому фото с caption+kb,
    видео отдельным сообщением (короткая подсказка про сохранение).
    """
    from bot.services.vpn_connect_copy import vpn_happ_region_video_caption_html

    video = happ_region_video_input(settings)
    if not video:
        _log.warning("happ_region_video_missing path=%s", HAPP_REGION_VIDEO_PATH)
        return False

    caption = (caption_html or vpn_happ_region_video_caption_html()).strip()
    if len(caption) > 1024:
        caption = caption[:1021] + "…"

    icon = happ_app_icon_input()
    uploaded_from_disk = isinstance(video, FSInputFile) or isinstance(icon, FSInputFile)
    video_hint = (
        "<i>Удержите видео → «Сохранить» или перешлите себе в «Избранное».</i>"
    )

    try:
        if icon is not None:
            photo_msg = await message.answer_photo(
                photo=icon,
                caption=caption,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
            _maybe_cache_ids(photo_msg, uploaded_from_disk=isinstance(icon, FSInputFile))
            video_msg = await message.answer_video(
                video=video,
                caption=video_hint,
                parse_mode="HTML",
            )
            _maybe_cache_ids(video_msg, uploaded_from_disk=isinstance(video, FSInputFile))
        else:
            video_msg = await message.answer_video(
                video=video,
                caption=caption,
                parse_mode="HTML",
                reply_markup=reply_markup,
            )
            _maybe_cache_ids(video_msg, uploaded_from_disk=isinstance(video, FSInputFile))
        return True
    except Exception:
        _log.exception("happ_region_video_send_failed")
        # Протухший file_id → сброс кэша и одна попытка с диска.
        cache = _load_file_id_cache()
        if cache and not isinstance(video, FSInputFile):
            try:
                path = _cache_path()
                if path.is_file():
                    path.unlink(missing_ok=True)
                _log.warning("happ_media_file_id_cache_cleared_after_send_fail")
            except OSError:
                pass
            if HAPP_REGION_VIDEO_PATH.is_file():
                try:
                    disk_video = FSInputFile(HAPP_REGION_VIDEO_PATH)
                    disk_icon = (
                        FSInputFile(HAPP_APP_ICON_PATH) if HAPP_APP_ICON_PATH.is_file() else None
                    )
                    if disk_icon is not None:
                        photo_msg = await message.answer_photo(
                            photo=disk_icon,
                            caption=caption,
                            parse_mode="HTML",
                            reply_markup=reply_markup,
                        )
                        _maybe_cache_ids(photo_msg, uploaded_from_disk=True)
                        video_msg = await message.answer_video(
                            video=disk_video,
                            caption=video_hint,
                            parse_mode="HTML",
                        )
                        _maybe_cache_ids(video_msg, uploaded_from_disk=True)
                    else:
                        video_msg = await message.answer_video(
                            video=disk_video,
                            caption=caption,
                            parse_mode="HTML",
                            reply_markup=reply_markup,
                        )
                        _maybe_cache_ids(video_msg, uploaded_from_disk=True)
                    return True
                except Exception:
                    _log.exception("happ_region_video_resend_from_disk_failed")
        return False
